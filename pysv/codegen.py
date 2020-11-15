from typing import Union, List
from .function import Function, DPIFunctionCall
from .types import DataType
from .model import PySVModel
import os
import sys

__INDENTATION = "  "
__GLOBAL_STRING_VAR_NAME = "string_result_value"
__PY_OBJ_MAP_NAME = "py_obj_map"
__SYS_PATH_NAME = "SYS_PATH"
__SYS_PATH_FUNC_NAME = "check_sys_path"


def __get_code_snippet(name):
    snippet_dir = os.path.join(os.path.dirname(__file__), "snippets")
    assert os.path.isdir(snippet_dir)
    filename = os.path.join(snippet_dir, name)
    assert os.path.exists(filename)
    with open(filename) as f:
        return f.read() + "\n"


def generate_dpi_definition(func_def: Union[Function, DPIFunctionCall],
                            pretty_print=True):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, Function), "Only " + Function.__name__ + " allowed"
    # generate args
    # python doesn't have output or ref semantics
    args = []
    for arg_name in func_def.arg_names:
        arg_type = func_def.arg_types[arg_name]
        arg_type_str = arg_type.value
        args.append("input {0} {1}".format(arg_type_str, arg_name))

    dpi_str = 'import "DPI-C" function'
    return_type_str = func_def.return_type.value
    func_name = func_def.func_name
    result = "{0} {1} {2}(".format(dpi_str, return_type_str, func_name)
    if pretty_print:
        padding = ",\n" + len(result) * " "
    else:
        padding = ", "
    arg_str = padding.join(args)
    result = "{0}{1});".format(result, arg_str)
    return result


def get_arg_name(name):
    return "__" + name


def __is_class_method(func_def: Union[Function, DPIFunctionCall]):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    return func_def.parent_class is not None


def __is_class_constructor(func_def: Union[Function, DPIFunctionCall]):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    return isinstance(func_def, PySVModel)


def __get_func_def(func_def: Union[Function, DPIFunctionCall]) -> Function:
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, Function)
    return func_def


def get_python_src(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    result = ""
    # 1. output the actual function body
    result += func_def.get_func_src() + "\n"

    # 2 add result call to set the result into locals
    # notice that we prefix __ to each arg using get_arg_name
    args = []
    for n in func_def.arg_names:
        if isinstance(func_def, PySVModel) and n == func_def.self_arg_name:
            # skip self in the python codegen
            continue
        args.append(get_arg_name(n))
    arg_str = ", ".join(args)
    if isinstance(func_def, PySVModel):
        # use the class name to instantiate the object
        func_name = func_def.__class__.__name__
    else:
        func_name = func_def.func_name
    result += "__result = {0}({1})\n".format(func_name, arg_str)

    return result


def get_c_type_str(data_type: DataType):
    if data_type == DataType.Bit:
        return "bool"
    elif data_type == DataType.Bit:
        return "int8_t"
    elif data_type == DataType.ShortInt:
        return "int16_t"
    elif data_type == DataType.Int:
        return "int32_t"
    elif data_type == DataType.LongInt:
        return "int64_t"
    elif data_type == DataType.UByte:
        return "uint8_t"
    elif data_type == DataType.UShortInt:
        return "uint16_t"
    elif data_type == DataType.UInt:
        return "uint32_t"
    elif data_type == DataType.ULongInt:
        return "uint64_t"
    elif data_type == DataType.CHandle:
        return "void*"
    elif data_type == DataType.String:
        return "const char*"
    elif data_type == DataType.Void:
        return "void"
    else:
        raise ValueError(data_type)


def get_c_function_signature(func_def: Union[Function, DPIFunctionCall], pretty_print=True, include_attribute=True):
    func_def = __get_func_def(func_def)
    return_type = get_c_type_str(func_def.return_type)
    if include_attribute:
        attribute = '__attribute__((visibility("default"))) '
    else:
        attribute = ""
    result = "{0}{1} {2}(".format(attribute, return_type, func_def.func_name)
    if pretty_print:
        padding = ",\n" + len(result) * " "
    else:
        padding = ", "
    args = []
    for name in func_def.arg_names:
        t = func_def.arg_types[name]
        t_str = get_c_type_str(t)
        args.append("{0} {1}".format(t_str, name))
    arg_str = padding.join(args)
    result = "{0}{1})".format(result, arg_str)
    return result


def generate_sys_path_check():
    return __INDENTATION + __SYS_PATH_FUNC_NAME + "();\n"


def generate_local_variables(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    result = __INDENTATION + "auto locals = py::dict();\n"
    # assigning values
    for n in func_def.arg_names:
        str_name = get_arg_name(n)
        s = __INDENTATION + 'locals["{0}"] = {1};\n'.format(str_name, n)
        result += s
    result += '\n'
    return result


def generate_global_variables(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    imports = func_def.imports
    # maybe there is a performance issue?
    # some modules may take some time to import.
    # if that is the case, maybe cache the imports somewhere?
    result = __INDENTATION + "auto globals = py::dict();\n"
    for n, m in imports.items():
        result += __INDENTATION + 'globals["{0}"] = py::module::import("{1}");;\n'.format(n, m)
    result += "\n"
    return result


def generate_execute_code(func_def: Union[Function, DPIFunctionCall], pretty_print=True):
    func_def = __get_func_def(func_def)
    # depends on whether it's class method or not
    if func_def.parent_class is not None:
        parent: PySVModel = func_def.parent_class
        # grab values from the locals
        arg_names = []
        for arg_name in parent.arg_names:
            if arg_name == parent.self_arg_name:
                # no need self
                continue
            arg = 'locals["{0}"]'.format(get_arg_name(arg_name))
            arg_names.append(arg)
        result = 'locals["__result"] = call_class_func('
        if pretty_print:
            padding = ",\n" + len(result) * " "
        else:
            padding = ", "
        args = padding.join(arg_names)
        result += args + ");\n"
    else:
        result = __INDENTATION + 'py::exec(R"(\n'
        python_src = get_python_src(func_def)
        result += python_src
        result += ')", globals, locals);\n'
    return result


def generate_return_value(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    result = __INDENTATION
    # notice that string is different since we need to use a global static
    # value to avoid memory leak
    return_type = func_def.return_type
    if return_type == DataType.Void:
        # nothing to be done for void return type
        return ""
    elif return_type == DataType.String:
        # special care for string
        result += '{0} = locals["__result"].cast<std::string>();\n'.format(__GLOBAL_STRING_VAR_NAME)
        result += __INDENTATION + "return {0}.c_str();\n".format(__GLOBAL_STRING_VAR_NAME)
    else:
        return_type_str = get_c_type_str(return_type)
        result += 'return locals["__result"].cast<{0}>();\n'.format(return_type_str)
    return result


def generate_cxx_function(func_def: Union[Function, DPIFunctionCall], pretty_print: bool = True,
                          add_sys_path: bool = True):
    result = get_c_function_signature(func_def, pretty_print)
    result += " {\n"
    result += generate_global_variables(func_def)
    result += generate_local_variables(func_def)
    if add_sys_path:
        result += generate_sys_path_check()
    result += generate_execute_code(func_def, pretty_print)
    result += generate_return_value(func_def)
    result += "}\n"

    return result


def generate_sys_path_values(pretty_print=True):
    result = "auto " + __SYS_PATH_NAME + " = {"
    if pretty_print:
        padding = ",\n" + len(result) * " "
    else:
        padding = ", "
    path_values = []
    for p in sys.path:
        path_values.append('"{0}"'.format(p))
    result += padding.join(path_values)
    result += "};\n\n"
    return result


def generate_bootstrap_code(pretty_print=True, add_sys_path=True, add_class=True):
    includes = ['"pybind11/include/pybind11/embed.h"',
                '"pybind11/include/pybind11/eval.h"']
    if add_class:
        includes += ['<iostream>',
                     '<unordered_map>']
    result = ""
    for file in includes:
        result += '#include {0}\n'.format(file)

    result += "namespace py = pybind11;\n"
    result += "py::scoped_interpreter guard;\n"
    result += "std::string {0};\n".format(__GLOBAL_STRING_VAR_NAME)
    if add_class:
        result += "std::unordered_map<void*, py::object> {0};\n".format(__PY_OBJ_MAP_NAME)
    if add_sys_path:
        result += generate_sys_path_values(pretty_print)
        result += __get_code_snippet("sys_path.cc")
    if add_class:
        result += __get_code_snippet("call_class_func.cc")
        result += __get_code_snippet("create_class_func.cc")

    return result


def generate_cxx_code(func_defs: List[Union[Function, DPIFunctionCall]], pretty_print: bool = True,
                      add_sys_path: bool = True, add_class: bool = True):
    result = generate_bootstrap_code(pretty_print, add_sys_path=add_sys_path, add_class=add_class) + "\n"
    # generate extern C block
    result += 'extern "C" {\n'
    code_blocks = []
    for func_def in func_defs:
        code_blocks.append(generate_cxx_function(func_def, pretty_print=pretty_print, add_sys_path=add_sys_path))
    result += "\n".join(code_blocks)
    result += "}\n"
    return result


def generate_c_header(func_def: Union[Function, DPIFunctionCall], pretty_print: bool = True):
    return get_c_function_signature(func_def, pretty_print=pretty_print,
                                    include_attribute=False) + ";"

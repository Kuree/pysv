from typing import Union, List
from .function import Function, DPIFunctionCall
from .types import DataType
from .model import check_class_ctor, get_dpi_functions, inject_destructor, check_class_method
from .util import should_add_class, should_add_sys_path
import os
import sys

__INDENTATION = "  "
__GLOBAL_STRING_VAR_NAME = "string_result_value"
__PY_OBJ_MAP_NAME = "py_obj_map"
__SYS_PATH_NAME = "SYS_PATH"
__SYS_PATH_FUNC_NAME = "check_sys_path"
__PYTHON_LIBRARY = "PYTHON_LIBRARY"


def __get_code_snippet(name):
    snippet_dir = os.path.join(os.path.dirname(__file__), "snippets")
    assert os.path.isdir(snippet_dir)
    filename = os.path.join(snippet_dir, name)
    assert os.path.exists(filename)
    with open(filename) as f:
        return f.read() + "\n"


def generate_dpi_signature(func_def: Union[Function, DPIFunctionCall],
                           pretty_print=True, is_class=False):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, Function), "Only " + Function.__name__ + " allowed"
    # generate args
    # python doesn't have output or ref semantics
    args = []
    for idx, arg_name in enumerate(func_def.arg_names):
        # skip the first one for function
        if (is_class or func_def.is_init) and idx == 0:
            continue
        arg_type = func_def.arg_types[arg_name]
        arg_type_str = arg_type.value
        args.append("input {0} {1}".format(arg_type_str, arg_name))

    if is_class:
        dpi_str = "function"
    else:
        dpi_str = 'import "DPI-C" function'

    if is_class and func_def.is_init:
        return_type_str = ""
    else:
        return_type_str = func_def.return_type.value

    if is_class:
        if func_def.is_init:
            func_name = "new"
        else:
            func_name = func_def.base_name
    else:
        func_name = func_def.func_name
    func_name += "("
    result = " ".join([s for s in [dpi_str, return_type_str, func_name] if s])
    if pretty_print:
        padding = ",\n" + len(result) * " "
    else:
        padding = ", "
    arg_str = padding.join(args)
    result = "{0}{1});".format(result, arg_str)
    return result


def generate_dpi_definitions(func_defs, pretty_print=True):
    new_defs = __get_func_defs(func_defs)
    result = ""
    for func in new_defs:
        result += "{0}\n".format(generate_dpi_signature(func, pretty_print))
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
    return func_def.is_init


def __get_func_def(func_def: Union[Function, DPIFunctionCall]) -> Function:
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, Function)
    return func_def


def __get_func_defs(func_defs):
    new_defs: List[DPIFunctionCall] = []
    for func in func_defs:
        if type(func) == type:
            funcs = get_dpi_functions(func)
            for f in funcs:
                new_defs.append(f)
        else:
            assert isinstance(func, DPIFunctionCall)
            new_defs.append(func)
    return new_defs


def __initialize_class_defs(func_defs):
    for func in func_defs:
        if type(func) == type:
            check_class_ctor(func)
            inject_destructor(func)
            check_class_method(func)


def get_python_src(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    result = ""
    # 1. output the actual function body
    result += func_def.get_func_src() + "\n"

    # 2 add result call to set the result into locals
    # notice that we prefix __ to each arg using get_arg_name
    args = []
    for idx, n in enumerate(func_def.arg_names):
        if func_def.is_init and idx == 0:
            # skip self in the python codegen
            continue
        args.append(get_arg_name(n))
    arg_str = ", ".join(args)
    if func_def.is_init:
        # use the class name to instantiate the object
        func_name = func_def.parent_class.__name__
    else:
        func_name = func_def.func_name
    result += "__result = {0}({1})\n".format(func_name, arg_str)

    return result


def get_c_type_str(data_type: DataType):  # pragma: no cover
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


def get_c_function_signature(func_def: Union[Function, DPIFunctionCall], pretty_print=True, include_attribute=True,
                             is_class=False, class_name="", split_return_type: bool = False):
    func_def = __get_func_def(func_def)
    return_type = get_c_type_str(func_def.return_type)
    if include_attribute:
        attribute = '__attribute__((visibility("default"))) '
    else:
        attribute = ""
    if is_class:
        if func_def.is_init:
            assert len(class_name) > 0
            func_name = class_name
            return_type = ""
        else:
            func_name = func_def.base_name
    else:
        func_name = func_def.func_name

    return_type = attribute + return_type
    if len(return_type) > 0 and not split_return_type:
        result = "{0} {1}(".format(return_type, func_name)
    else:
        result = func_name + "("
    if pretty_print:
        padding = ",\n" + len(result) * " "
        if is_class:
            padding += __INDENTATION
    else:
        padding = ", "
    args = []
    for idx, name in enumerate(func_def.arg_names):
        if (is_class or func_def.is_init) and idx == 0:
            # class constructor don't need the first self
            continue
        t = func_def.arg_types[name]
        t_str = get_c_type_str(t)
        args.append("{0} {1}".format(t_str, name))
    arg_str = padding.join(args)
    result = "{0}{1})".format(result, arg_str)
    if split_return_type:
        return return_type, result
    else:
        return result


def generate_sys_path_check():
    # need to figure out the python lib users are currently using
    return __INDENTATION + __SYS_PATH_FUNC_NAME + '({0});\n'.format(__PYTHON_LIBRARY)


def generate_local_variables(func_def: Union[Function, DPIFunctionCall]):
    func_def = __get_func_def(func_def)
    result = __INDENTATION + "auto locals = py::dict();\n"
    # assigning values
    for idx, n in enumerate(func_def.arg_names):
        if func_def.is_init and idx == 0:
            # class constructor don't need the first self
            continue
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
    if func_def.parent_class is not None and not func_def.is_init:
        # grab values from the locals
        arg_names = [func_def.arg_names[0], '"{0}"'.format(func_def.base_name)]
        for arg_name in func_def.arg_names[1:]:
            arg = 'locals["{0}"]'.format(get_arg_name(arg_name))
            arg_names.append(arg)
        result = __INDENTATION + 'locals["__result"] = call_class_func('
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
    result = ""
    # notice that string is different since we need to use a global static
    # value to avoid memory leak
    return_type = func_def.return_type
    if return_type == DataType.Void:
        # nothing to be done for void return type
        return ""
    elif return_type == DataType.String:
        # special care for string
        result += __INDENTATION + '{0} = locals["__result"].cast<std::string>();\n'.format(__GLOBAL_STRING_VAR_NAME)
        result += __INDENTATION + "return {0}.c_str();\n".format(__GLOBAL_STRING_VAR_NAME)
    elif return_type == DataType.CHandle:
        # need to call the cxx function
        result += __INDENTATION + "return create_class_func(locals);\n"
    else:
        return_type_str = get_c_type_str(return_type)
        result += __INDENTATION + 'return locals["__result"].cast<{0}>();\n'.format(return_type_str)
    return result


def generate_cxx_function(func_def: Union[Function, DPIFunctionCall], pretty_print: bool = True,
                          add_sys_path: bool = True):
    result = get_c_function_signature(func_def, pretty_print)
    result += " {\n"
    if add_sys_path:
        result += generate_sys_path_check()
    result += generate_global_variables(func_def)
    result += generate_local_variables(func_def)
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
    result = __get_code_snippet("include_header.hh")

    result += "namespace py = pybind11;\n"
    if not add_sys_path:
        result += "py::scoped_interpreter guard;\n"
    result += "std::string {0};\n".format(__GLOBAL_STRING_VAR_NAME)

    if add_class:
        result += "std::unordered_map<void*, py::object> {0};\n".format(__PY_OBJ_MAP_NAME)
    if add_sys_path:
        result += __get_code_snippet("initialize_guard.cc")
        result += generate_sys_path_values(pretty_print)
        result += __get_code_snippet("sys_path.cc")
    if add_class:
        result += __get_code_snippet("call_class_func.cc")
        result += __get_code_snippet("create_class_func.cc")

    return result


def generate_pybind_code(func_defs: List[Union[type, DPIFunctionCall]], pretty_print: bool = True,
                         namespace: str = "pysv", add_sys_path: bool = False):
    add_class = should_add_class(func_defs)
    if not add_sys_path:
        add_sys_path = should_add_class(func_defs)
    result = generate_bootstrap_code(pretty_print, add_sys_path=add_sys_path, add_class=add_class) + "\n"
    # generate extern C block
    result += 'extern "C" {\n'
    code_blocks = []
    # initialize the check the classes
    __initialize_class_defs(func_defs)
    new_defs = __get_func_defs(func_defs)
    for func_def in new_defs:
        code_blocks.append(generate_cxx_function(func_def, pretty_print=pretty_print, add_sys_path=add_sys_path))
    result += "\n".join(code_blocks)
    result += "}\n"

    # notice that if there is classes involved, we also need to generate the class implementation
    if add_class:
        result += generate_cxx_binding(func_defs, pretty_print=pretty_print, include_implementation=True,
                                       namespace=namespace)

    return result


def generate_c_header(func_def: Union[Function, DPIFunctionCall], pretty_print: bool = True):
    return get_c_function_signature(func_def, pretty_print=pretty_print,
                                    include_attribute=False) + ";"


def generate_c_headers(func_defs, pretty_print: bool = True):
    headers = []
    for func_def in func_defs:
        if type(func_def) == type:
            funcs = get_dpi_functions(func_def)
            for f in funcs:
                headers.append(generate_c_header(f, pretty_print))
        else:
            headers.append(generate_c_header(func_def, pretty_print))
    result = "#include <iostream>\n"
    result += 'extern "C" {\n'
    result += "\n".join(headers)
    result += "\n}\n"
    return result


def generate_sv_class(func_def, pretty_print: bool = True):
    result = ""
    cls = func_def
    assert cls is not None
    class_name = cls.__name__
    funcs = get_dpi_functions(cls)
    result += "class {0};\n".format(class_name)
    # a local chandle
    chandle_name = "pysv_ptr"
    result += __INDENTATION + "local chandle {0};\n".format(chandle_name)
    for func in funcs:
        sig = generate_dpi_signature(func, pretty_print=pretty_print, is_class=True)
        result += __INDENTATION + sig + "\n"
        # generate the call
        args = [chandle_name] + func.func_def.arg_names[1:]
        if func.func_def.is_init:
            # don't need to first self
            args = args[1:]
        args = ", ".join(args)
        if func.func_def.is_init:
            var_assign = chandle_name + " = "
        else:
            if func.func_def.return_type != DataType.Void:
                var_assign = "return "
            else:
                var_assign = ""
        result += __INDENTATION * 2 + var_assign + func.func_def.func_name + "({0});\n".format(args)
        result += __INDENTATION + "endfunction\n"

    result += "endclass\n"
    return result


def generate_sv_binding(func_defs: List[Union[type, DPIFunctionCall]], pkg_name="", pretty_print: bool = True,
                        filename=None):
    if len(pkg_name) == 0:
        pkg_name = "pysv"
    guard_name = "PYSV_" + pkg_name.upper()
    result = ""
    # generate the guard
    result += "`ifndef {0}\n".format(guard_name)
    result += "`define {0}\n".format(guard_name)

    # package
    result += "package {0};\n".format(pkg_name)

    __initialize_class_defs(func_defs)

    # produce DPI imports
    result += generate_dpi_definitions(func_defs, pretty_print)

    # generate class definition
    for func_def in func_defs:
        if type(func_def) == type:
            result += generate_sv_class(func_def, pretty_print)

    # end of package
    result += "endpackage\n"
    # end of guard
    result += "`endif // {0}\n".format(guard_name)

    if filename is not None:
        with open(filename, "w+") as f:
            f.write(result)

    return result


def generate_cxx_class(cls, pretty_print: bool = True, include_implementation: bool = False):
    result = ""
    assert cls is not None
    class_name = cls.__name__
    result += "class {0} {{\n".format(class_name)

    # a local pointer
    pointer_name = "pysv_ptr"

    result += "private:\n"
    result += __INDENTATION + "void *{0};\n".format(pointer_name)

    result += "public:\n"
    # generating methods
    func_defs = get_dpi_functions(cls)
    for func in func_defs:
        result += __INDENTATION + get_c_function_signature(func, pretty_print, include_attribute=include_implementation,
                                                           is_class=True, class_name=class_name) + ";\n"

    result += "};\n"

    if include_implementation:
        for func in func_defs:
            return_type, sig = get_c_function_signature(func, pretty_print, include_attribute=False, is_class=True,
                                                        class_name=class_name, split_return_type=True)
            result += "{0} {1}::{2}".format(return_type, class_name, sig)
            result += " {\n"
            # call the wrapper function
            func_name = func.func_def.func_name
            # generate the call
            args = [pointer_name] + func.func_def.arg_names[1:]
            if func.func_def.is_init:
                args = args[1:]
            args = "{0}({1});".format(func_name, ", ".join(args))
            tokens = []
            if func.func_def.is_init:
                tokens.append(pointer_name)
                tokens.append("=")
            elif func.func_def.return_type != DataType.Void:
                tokens.append("return")
            tokens.append(args)
            result += __INDENTATION * 2 + " ".join(tokens) + "\n"
            result += __INDENTATION + "}\n"

    return result


def generate_cxx_binding(func_defs: List[Union[type, DPIFunctionCall]], pretty_print: bool = True,
                         filename=None, include_implementation: bool = False, namespace: str = "pysv"):
    if filename is not None:
        header_name = os.path.basename(filename)
        header_name = header_name.replace(".", "_").replace("-", "_")
        header_name = header_name.upper()
    else:
        header_name = "PYSV_CXX_BINDING"

    result = ""
    # include guard
    result += "#ifndef {0}\n".format(header_name)
    result += "#define {0}\n".format(header_name)

    # initialize the class if not done yet
    __initialize_class_defs(func_defs)

    # need to generate the C includes
    if not include_implementation:
        result += generate_c_headers(func_defs, pretty_print)

    # need to output namespace
    result += "namespace {0} {{\n".format(namespace)

    # generate c++ classes
    for func_def in func_defs:
        if type(func_def) == type:
            result += generate_cxx_class(func_def, pretty_print, include_implementation)

    # end of namespace
    result += "}\n"

    # end of include guard
    result += "#endif // {0}\n".format(header_name)

    if filename is not None:
        with open(filename, "w+") as f:
            f.write(result)

    return result

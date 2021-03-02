from typing import Union, List
from .function import Function, DPIFunctionCall, sv
from .types import DataType
from .model import check_class_ctor, get_dpi_functions, inject_destructor, check_class_method
from .util import (should_add_class, should_add_sys_path, make_dirs, make_unique_func_defs, should_import, is_conda,
                   is_class)
import os
import sys

__INDENTATION = "  "
__GLOBAL_STRING_VAR_NAME = "string_result_value"
__PY_OBJ_MAP_NAME = "py_obj_map"
__SYS_PATH_NAME = "SYS_PATH"
__SYS_PATH_FUNC_NAME = "check_sys_path"
__CHECK_INTERPRETER = "check_interpreter"
__PYTHON_LIBRARY = "PYTHON_LIBRARY"
__IMPORT_MODULE = "import_module"
__GET_LOCAL_OBJECT = "get_local_object"
__PYSV_OBJECT_BASE = "PySVObject"
__PYSV_DESTROY = "destroy"
__LOAD_CLASS_DEFS = "load_class_defs"
__DEFAULT_ATTRIBUTE = '__attribute__((visibility("default"))) '


def __get_code_snippet(name):
    snippet_dir = os.path.join(os.path.dirname(__file__), "snippets")
    assert os.path.isdir(snippet_dir)
    filename = os.path.join(snippet_dir, name)
    assert os.path.exists(filename)
    with open(filename) as f:
        return f.read() + "\n"


def __should_include_local_object(func_defs):
    func_defs = __get_func_defs(func_defs)
    for func_def in func_defs:
        func_def = __get_func_def(func_def)
        start_idx = 0 if func_def.parent_class is None else 1
        for idx, name in enumerate(func_def.arg_names):
            if idx < start_idx:
                continue
            arg_type = func_def.arg_types[name]
            if arg_type == DataType.Object:
                return True
    return False


def __get_conda_path():
    result = ""
    if is_conda():
        python_home = os.path.dirname(sys.executable)
        python_path = ":".join(sys.path)
        result += "std::string conda_python_home = \"{0}\"\n;".format(python_home)
        result += "std::string conda_python_path = \"{0}\";\n".format(python_path)
    else:
        result += "std::string conda_python_home;\n"
        result += "std::string conda_python_path;\n"
    return result


def generate_dpi_signature(func_def: Union[Function, DPIFunctionCall],
                           pretty_print=True, is_class=False, is_function_class_wrapper=False,
                           ref_ctor_name=""):
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
        if (is_class or is_function_class_wrapper) and arg_type == DataType.Object:
            if arg_name in func_def.arg_obj_ref:
                arg_type_str = func_def.arg_obj_ref[arg_name].__name__
            else:
                arg_type_str = __PYSV_OBJECT_BASE
        else:
            arg_type_str = arg_type.value
        args.append("input {0} {1}".format(arg_type_str, arg_name))
    # notice that we generate output at the end
    for arg_name in func_def.output_names:
        # we only allow primitive data types for return reference type
        arg_type = func_def.arg_types[arg_name]
        arg_type_str = arg_type.value
        args.append("output {0} {1}".format(arg_type_str, arg_name))

    # additional signature for ref ctor
    if is_class and len(ref_ctor_name) > 0 and func_def.is_init:
        args.append("input chandle {0}=null".format(ref_ctor_name))

    if is_class or is_function_class_wrapper:
        dpi_str = "function"
    else:
        dpi_str = 'import "DPI-C" function'

    if is_class and func_def.is_init:
        return_type_str = ""
    elif (is_class or is_function_class_wrapper) and func_def.return_type == DataType.Object:
        if func_def.return_obj_ref is not None:
            return_type_str = func_def.return_obj_ref.__name__
        else:
            return_type_str = __PYSV_OBJECT_BASE
    else:
        return_type_str = func_def.return_type.value

    if is_class:
        if func_def.is_init:
            func_name = "new"
        else:
            func_name = func_def.base_name
    else:
        if is_function_class_wrapper:
            func_name = func_def.base_name
        else:
            func_name = func_def.func_name
    func_name += "("
    result = " ".join([s for s in [dpi_str, return_type_str, func_name] if s])
    if pretty_print:
        padding = ",\n" + len(result) * " "
        if is_class:
            padding += __INDENTATION
    else:
        padding = ", "
    arg_str = padding.join(args)
    result = "{0}{1});".format(result, arg_str)
    return result


def generate_dpi_definitions(func_defs, pretty_print=True):
    if pysv_finalize not in func_defs:
        func_defs = func_defs + [pysv_finalize]
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
        if is_class(func):
            funcs = get_dpi_functions(func)
            for f in funcs:
                new_defs.append(f)
        else:
            new_defs.append(func)
    return new_defs


def __initialize_class_defs(func_defs):
    for func in func_defs:
        if is_class(func):
            check_class_ctor(func)
            inject_destructor(func)
            check_class_method(func)


def __has_imports(func_defs):
    for func in func_defs:
        if is_class(func):
            fs = get_dpi_functions(func)
            f: DPIFunctionCall
            for f in fs:
                if len(f.func_def.imports) > 0:
                    return True
        else:
            func_def = __get_func_def(func)
            if len(func_def.imports) > 0:
                return True
    return False


def __get_forwarded_types(func_defs):
    result = []
    new_func_defs = __get_func_defs(func_defs)
    for func_def in new_func_defs:
        func_def = __get_func_def(func_def)
        cls_list = []
        if func_def.return_obj_ref is not None:
            cls_list.append(func_def.return_obj_ref)
        for t in func_def.arg_obj_ref.values():
            cls_list.append(t)
        for t in cls_list:
            assert t in func_defs, "sv class reference ({0}) as to be in the generate list".format(t.__name__)
            if t not in result:
                result.append(t)
    return result


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
        func_name = func_def.base_name
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
    elif data_type == DataType.Object:
        return "void*"
    elif data_type == DataType.String:
        return "const char*"
    elif data_type == DataType.Void:
        return "void"
    else:
        raise ValueError(data_type)


def get_c_function_signature(func_def: Union[Function, DPIFunctionCall], pretty_print=True, include_attribute=True,
                             is_class=False, is_function_class_wrapper=False, class_name="",
                             split_return_type: bool = False):
    func_def = __get_func_def(func_def)
    return_type = get_c_type_str(func_def.return_type)
    if include_attribute:
        attribute = __DEFAULT_ATTRIBUTE
    else:
        attribute = ""
    if is_class or is_function_class_wrapper:
        if is_class:
            assert len(class_name) > 0
        if func_def.is_init:
            func_name = class_name
            return_type = ""
        else:
            # special case for destructor
            if func_def.base_name == __PYSV_DESTROY:
                func_name = "~" + class_name
                return_type = ""
            else:
                func_name = func_def.base_name
                # return as object
                if func_def.return_type == DataType.Object:
                    if func_def.return_obj_ref is not None:
                        return_type = func_def.return_obj_ref.__name__
                    else:
                        return_type = __PYSV_OBJECT_BASE
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
        if (is_class or is_function_class_wrapper) and t == DataType.Object:
            if name in func_def.arg_obj_ref:
                cls_name = func_def.arg_obj_ref[name].__name__
            else:
                cls_name = __PYSV_OBJECT_BASE
            t_str = cls_name + "*"
        else:
            t_str = get_c_type_str(t)
        args.append("{0} {1}".format(t_str, name))
    # generate output args
    for name in func_def.output_names:
        t = func_def.arg_types[name]
        t_str = get_c_type_str(t)
        args.append("{0} *{1}".format(t_str, name))
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
        arg_type = func_def.arg_types[n]
        if arg_type == DataType.Object and not (idx == 0 and func_def.parent_class is not None):
            s = __INDENTATION + __GET_LOCAL_OBJECT + '("{0}", {1}, locals);\n'.format(str_name, n)
        else:
            s = __INDENTATION + 'locals["{0}"] = {1};\n'.format(str_name, n)
        result += s
    result += '\n'
    return result


def generate_global_variables(func_def: Union[Function, DPIFunctionCall], add_class=False):
    func_def = __get_func_def(func_def)
    raw_imports = func_def.imports
    imports = {}
    py_src = func_def.get_func_src(False)
    for n, m in raw_imports.items():
        if should_import(n, py_src):
            imports[n] = m
    result = __INDENTATION + "auto globals = py::dict();\n"
    if add_class:
        result += __INDENTATION + __LOAD_CLASS_DEFS + "(globals);\n"
    if len(imports) > 0:
        for n, m in imports.items():
            result += __INDENTATION + '{0}("{1}", "{2}", globals);\n'.format(__IMPORT_MODULE, m, n)
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
        # we have some complication here
        # if the user is returning a reference, we need to unpack the tuple and set the value properly
        if len(func_def.output_names) == 1:
            t_str = get_c_type_str(func_def.arg_types[func_def.output_names[0]])
            result += __INDENTATION + '*{0} = locals["__result"].cast<{1}>();\n'.format(func_def.output_names[0], t_str)
        elif len(func_def.output_names) > 1:
            result += __INDENTATION + 'auto ref_result = locals["__result"].cast<py::list>();\n'
            # generate error checking at runtime
            result += __INDENTATION + 'if (py::len(ref_result) != {0}) {{\n'.format(len(func_def.output_names))
            result += __INDENTATION * 2 + 'throw std::runtime_error("Invalid return tuple size");\n'
            result += __INDENTATION + "}\n"
            # now generate the value setting part
            for idx, arg_name in enumerate(func_def.output_names):
                t_str = get_c_type_str(func_def.arg_types[arg_name])
                result += __INDENTATION + '*{0} = ref_result[{1}].cast<{2}>();\n'.format(arg_name, idx, t_str)
        else:
            # nothing to be done for void return type
            return ""
    elif return_type == DataType.String:
        # special care for string
        result += __INDENTATION + '{0} = locals["__result"].cast<std::string>();\n'.format(__GLOBAL_STRING_VAR_NAME)
        result += __INDENTATION + "return {0}.c_str();\n".format(__GLOBAL_STRING_VAR_NAME)
    elif return_type == DataType.Object:
        # need to call the cxx function
        if func_def.is_init:
            class_name = func_def.parent_class.__name__
        else:
            class_name = ""
        result += __INDENTATION + 'return create_class_func(locals, "{0}");\n'.format(class_name)
    else:
        return_type_str = get_c_type_str(return_type)
        result += __INDENTATION + 'return locals["__result"].cast<{0}>();\n'.format(return_type_str)
    return result


def generate_check_interpreter():
    return __INDENTATION + __CHECK_INTERPRETER + "();\n"


def generate_cxx_function(func_def: Union[Function, DPIFunctionCall], pretty_print: bool = True,
                          add_sys_path: bool = True, add_class: bool = True):
    result = get_c_function_signature(func_def, pretty_print)
    result += " {\n"
    if add_sys_path:
        result += generate_sys_path_check()
    else:
        result += generate_check_interpreter()
    result += generate_global_variables(func_def, add_class=add_class)
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


def generate_bootstrap_code(pretty_print=True, add_sys_path=True, add_class=True, add_imports=True,
                            add_local_object=True):
    result = __get_code_snippet("include_header.hh")
    result += __get_code_snippet("runtime_values.cc")

    if add_sys_path:
        result += __get_conda_path()
        result += __get_code_snippet("initialize_guard.cc")
        result += generate_sys_path_values(pretty_print)
        result += __get_code_snippet("sys_path.cc")
    else:
        result += __get_code_snippet("check_interpreter.cc")
    if add_class:
        result += __get_code_snippet("call_class_func.cc")
        result += __get_code_snippet("create_class_func.cc")
        result += __get_code_snippet("load_class_defs.cc")
    if add_imports:
        result += __get_code_snippet("import_global.cc")
    if add_local_object:
        result += __get_code_snippet("get_local_object.cc")

    return result


def pysv_finalize():
    # a dummy to allow runtime to be reset
    pass


pysv_finalize = sv()(pysv_finalize)


def generate_runtime_finalize(pretty_print):
    result = get_c_function_signature(pysv_finalize, pretty_print) + " {\n"
    result += __get_code_snippet("finalize_runtime.cc")
    result += "}\n"
    return result


def generate_forward_sv_class_definition(class_refs):
    result = ""
    for cls in class_refs:
        result += "typedef class {0};\n".format(cls.__name__)

    return result


def generate_pybind_code(func_defs: List[Union[type, DPIFunctionCall]], pretty_print: bool = True,
                         namespace: str = "pysv", add_sys_path: bool = False):
    # initialize the check the classes
    __initialize_class_defs(func_defs)
    # remove unnecessary entries
    func_defs = make_unique_func_defs(func_defs)

    add_class = should_add_class(func_defs)
    if not add_sys_path:
        add_sys_path = should_add_sys_path(func_defs)
    add_imports = __has_imports(func_defs)
    add_local_object = __should_include_local_object(func_defs)
    result = generate_bootstrap_code(pretty_print, add_sys_path=add_sys_path, add_class=add_class,
                                     add_imports=add_imports, add_local_object=add_local_object) + "\n"
    # generate extern C block
    result += 'extern "C" {\n'
    code_blocks = []

    new_defs = __get_func_defs(func_defs)
    for func_def in new_defs:
        code_blocks.append(generate_cxx_function(func_def, pretty_print=pretty_print, add_sys_path=add_sys_path,
                                                 add_class=add_class))
    result += "\n".join(code_blocks)
    result += generate_runtime_finalize(pretty_print=pretty_print)
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
    # finalize is a built-in function
    if pysv_finalize not in func_defs:
        func_defs = func_defs + [pysv_finalize]
    func_defs = make_unique_func_defs(func_defs)
    for func_def in func_defs:
        if is_class(func_def):
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


def __get_function_call_args(func, ptr_name, is_sv=True, is_class=True):
    func = __get_func_def(func)
    arg_names = []
    args = func.arg_names[1:] if is_class else func.arg_names
    for arg_name in args:
        arg_type = func.arg_types[arg_name]
        if arg_type == DataType.Object:
            access = "." if is_sv else "->"
            arg_names.append("{0}{1}{2}".format(arg_name, access, ptr_name))
        else:
            arg_names.append(arg_name)
    return arg_names


def __get_init_call_dummy_args(func_def):
    func_def = __get_func_def(func_def)
    arg_types = func_def.arg_types
    result = []
    for name in func_def.arg_names[1:]:
        t = arg_types[name]
        if t == DataType.String:
            result.append('""')
        elif t == DataType.Object:
            result.append("null")
        else:
            result.append("0")
    return result


def generate_sv_function_with_class(func_defs, pretty_print: bool = True):
    result = ""
    for func_def in func_defs:
        if not isinstance(func_def, sv):
            continue
        if func_def.parent_class is None and func_def.has_obj_ref():
            result += generate_sv_class_method(func_def, pretty_print=pretty_print, is_class=False)
    return result


def generate_cxx_function_with_class(func_defs, include_implementation: bool = False,
                                     pretty_print: bool = True):
    result = ""
    for func_def in func_defs:
        if not isinstance(func_def, sv):
            continue
        if func_def.parent_class is None and func_def.has_obj_ref():
            if include_implementation:
                result += generate_cxx_class_method(func_def, is_class=False, class_name="", pretty_print=pretty_print)
            else:
                result += get_c_function_signature(func_def, pretty_print, include_attribute=False, is_class=False,
                                                   is_function_class_wrapper=True) + ";\n"
    return result


def generate_cxx_class_method(func, is_class, class_name, pretty_print=True):
    func = __get_func_def(func)
    if is_class:
        assert len(class_name) > 0
    # a local pointer
    pointer_name = "pysv_ptr"
    result = ""
    return_type, sig = get_c_function_signature(func, pretty_print, include_attribute=not is_class, is_class=is_class,
                                                class_name=class_name, split_return_type=True,
                                                is_function_class_wrapper=not is_class)
    if is_class:
        if len(return_type) > 0:
            result += "{0} {1}::{2}".format(return_type, class_name, sig)
        else:
            result += "{0}::{1}".format(class_name, sig)
    else:
        result += "{0} {1}".format(return_type, sig)
    result += " {\n"
    # call the wrapper function
    func_name = func.func_name
    # generate the call
    arg_names = __get_function_call_args(func, pointer_name, is_sv=False, is_class=is_class)
    if is_class:
        args = [pointer_name] + arg_names
    else:
        args = arg_names
    if func.is_init:
        args = args[1:]
    args = "{0}({1});".format(func_name, ", ".join(args))
    tokens = []
    if func.is_init:
        tokens.append(pointer_name)
        tokens.append("=")
    elif func.return_type != DataType.Void:
        if func.return_type == DataType.Object:
            tokens += ["auto", "ptr__", "="]
        else:
            tokens.append("return")
    tokens.append(args)
    result += __INDENTATION * 2 + " ".join(tokens) + "\n"
    # return a pyobject wrapper
    if not func.is_init and func.return_type == DataType.Object:
        if func.return_obj_ref is not None:
            cls_name = func.return_obj_ref.__name__
        else:
            cls_name = __PYSV_OBJECT_BASE
        result += __INDENTATION * 2 + "return {0}({1});\n".format(cls_name, "ptr__")
    result += "}\n"

    return result


def generate_sv_class_method(func, pretty_print: bool = True, ref_ctor: bool = False, is_class: bool = True):
    func = __get_func_def(func)
    # use protected chandle from the base class
    chandle_name = "pysv_ptr"
    class_ref_ctor_name = "ptr"
    ref_ctor_name = class_ref_ctor_name if ref_ctor else ""
    result = ""
    if is_class:
        base_indentation = __INDENTATION
        indentation = __INDENTATION * 2
    else:
        base_indentation = ""
        indentation = __INDENTATION
    sig = generate_dpi_signature(func, pretty_print=pretty_print, is_class=is_class, ref_ctor_name=ref_ctor_name,
                                 is_function_class_wrapper=not is_class)
    result += base_indentation + sig + "\n"
    # generate the call
    arg_names = __get_function_call_args(func, chandle_name, is_class=is_class)
    if is_class:
        args = [chandle_name] + arg_names
    else:
        args = arg_names
    if func.is_init:
        # don't need to first self
        args = args[1:]
    args = ", ".join(args)
    # need to declare variables first
    if func.is_init:
        # this is the constructor
        if ref_ctor:
            # special case to call constructor differently
            # need to generate an if statement
            result += """{0}{0}if ({1} == null) begin
{0}{0}{0}{2} = {3}({4});
{0}{0}end
{0}{0}else begin
{0}{0}{0}{2} = {1};
{0}{0}end\n""".format(base_indentation, class_ref_ctor_name, chandle_name, func.func_name, args)
        else:
            # normal function call
            result += indentation + "{0} = {1}({2});\n".format(chandle_name, func.func_name, args)
    else:
        if func.return_type == DataType.Object and (not func.is_init):
            if func.return_obj_ref is not None:
                # we are actually creating this one
                init_func = func.return_obj_ref.__init__
                init_args = __get_init_call_dummy_args(init_func)
                # generate code
                result += indentation + "chandle {0};\n".format(class_ref_ctor_name)
                result += indentation + "{0} ptr__;\n".format(func.return_obj_ref.__name__)
                result += indentation + "{0} = {1}({2});\n".format(class_ref_ctor_name,
                                                                   func.func_name, args)
                init_args.append(class_ref_ctor_name)
                result += indentation + "ptr__ = new({0});\n".format(", ".join(init_args))
                result += indentation + "return ptr__;\n"
            else:
                # return normal PySVObject instead
                result += indentation + "{0} obj__;\n".format(__PYSV_OBJECT_BASE)
                result += indentation + "chandle ptr__;\n"
                result += indentation + "ptr__ = {0}({1});\n".format(func.func_name, args)
                result += indentation + "obj__ = new();\n"
                result += indentation + "obj__.{0} = ptr__;\n".format(chandle_name)
                result += indentation + "return obj__;\n"
        else:
            if func.return_type == DataType.Void:
                result += indentation + "{0}({1});\n".format(func.func_name, args)
            else:
                result += indentation + "return {0}({1});\n".format(func.func_name, args)
    result += base_indentation + "endfunction\n"
    return result


def generate_sv_class(func_def, pretty_print: bool = True, ref_ctor: bool = False):
    result = ""
    cls = func_def
    assert cls is not None
    class_name = cls.__name__
    funcs = get_dpi_functions(cls)
    result += "class {0} extends {1};\n".format(class_name, __PYSV_OBJECT_BASE)
    for func in funcs:
        result += generate_sv_class_method(func, pretty_print=pretty_print, ref_ctor=ref_ctor)

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
    func_defs = make_unique_func_defs(func_defs)

    # produce DPI imports
    result += generate_dpi_definitions(func_defs, pretty_print)

    # generate class definition
    # test if we need to generate class
    has_class = should_add_class(func_defs)
    if has_class:
        result += __get_code_snippet("pysv_object_base.sv")
        class_refs = __get_forwarded_types(func_defs)
        # need to generate forward definition if needed
        result += generate_forward_sv_class_definition(class_refs)
        for func_def in func_defs:
            if is_class(func_def):
                result += generate_sv_class(func_def, pretty_print, func_def in class_refs)
        # any function takes in class as well
        result += generate_sv_function_with_class(func_defs, pretty_print=pretty_print)

    # end of package
    result += "endpackage\n"
    # end of guard
    result += "`endif // {0}\n".format(guard_name)

    if filename is not None:
        make_dirs(filename)
        with open(filename, "w+") as f:
            f.write(result)

    return result


def generate_cxx_class(cls, pretty_print: bool = True, include_implementation: bool = False, ref_ctor: bool = False):
    result = ""
    assert cls is not None
    class_name = cls.__name__
    result += "class {0} : public {1} {{\n".format(class_name, __PYSV_OBJECT_BASE)

    result += "public:\n"
    # generating methods
    func_defs = get_dpi_functions(cls)
    for func in func_defs:
        sig = get_c_function_signature(func, pretty_print, include_attribute=include_implementation,
                                       is_class=True, class_name=class_name)
        if func.func_def.base_name == __PYSV_DESTROY:
            sig += " override"

        result += __INDENTATION + sig + ";\n"
    # generate the extra constructor to deal with ref class
    if ref_ctor:
        attr = __DEFAULT_ATTRIBUTE if include_implementation else ""
        result += __INDENTATION + attr + "inline {0}(void *ptr): {1}(ptr) {{}}\n".format(class_name,
                                                                                         __PYSV_OBJECT_BASE)

    result += "};\n"

    if include_implementation:
        for func in func_defs:
            result += generate_cxx_class_method(func, is_class=True, class_name=class_name, pretty_print=pretty_print)

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

    # remove the unnecessary entries
    func_defs = make_unique_func_defs(func_defs)
    # initialize the class if not done yet
    __initialize_class_defs(func_defs)

    # need to generate the C includes
    if not include_implementation:
        result += generate_c_headers(func_defs, pretty_print)

    # need to output namespace
    result += "namespace {0} {{\n".format(namespace)

    # generate c++ classes
    add_class = should_add_class(func_defs)
    if add_class:
        result += __get_code_snippet("cxx_object_base.cc")
        class_refs = __get_forwarded_types(func_defs)
        for func_def in func_defs:
            if is_class(func_def):
                result += generate_cxx_class(func_def, pretty_print, include_implementation,
                                             ref_ctor=func_def in class_refs)
        result += generate_cxx_function_with_class(func_defs, include_implementation=include_implementation,
                                                   pretty_print=pretty_print)

    # end of namespace
    result += "}\n"

    # end of include guard
    result += "#endif // {0}\n".format(header_name)

    if filename is not None:
        make_dirs(filename)
        with open(filename, "w+") as f:
            f.write(result)

    return result

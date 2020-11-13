from typing import Union
from .function import DPIFunction, DPIFunctionCall


def get_dpi_definition(func_def: Union[DPIFunction, DPIFunctionCall],
                       pretty_print=True):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, DPIFunction), "Only " + DPIFunction.__name__ + " allowed"
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


def get_python_src(func_def: Union[DPIFunction, DPIFunctionCall]):
    if isinstance(func_def, DPIFunctionCall):
        func_def = func_def.func_def
    assert isinstance(func_def, DPIFunction)
    result = ""
    # 1. generate the imports
    imports = func_def.imports
    # maybe there is a performance issue?
    # some modules may take some time to import.
    # if that is the case, maybe cache the imports somewhere?
    for n, m in imports.items():
        if n == m:
            result += "import {0}\n".format(n)
        else:
            result += "import {0} as {1}\n".format(m, n)

    # 2. output the actual function body
    result += func_def.get_func_src() + "\n"

    # 3 add result call to set the result into locals
    # notice that we prefix __ to each arg using get_arg_name
    args = []
    for n in func_def.arg_names:
        args.append(get_arg_name(n))
    arg_str = ", ".join(args)
    result += "__result = {0}({1})\n".format(func_def.func_name, arg_str)

    return result

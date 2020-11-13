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


def get_python_src(func_def: DPIFunction):
    result = ""
    # 1. generate the imports
    imports = func_def.imports


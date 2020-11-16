import inspect
from .function import DPIFunctionCall, DPIFunction
from .types import DataType


def get_dpi_functions(cls: type):
    attrs = [(a, getattr(cls, a)) for a in dir(cls)]
    result = []
    for attr_name, attr in attrs:
        if isinstance(attr, DPIFunctionCall):
            result.append(attr)
            # set init as well
            if attr_name == "__init__":
                attr.func_def.is_init = True
                # return type is c_handle
                attr.func_def.return_type = DataType.CHandle
            else:
                # normal function call
                # set the first argument to be chandle
                attr.func_def.arg_types[attr.func_def.arg_names[0]] = DataType.CHandle
    return result


def check_class_ctor(cls: type):
    ctor = cls.__init__
    if not isinstance(ctor, DPIFunctionCall):
        # it's a normal init ctor
        # make sure that it doesn't have any extra parameters
        signature = inspect.signature(ctor)
        assert len(signature.parameters) == 1, """Class constructor has more arguments than simple
self is required to have @sv decorator"""
        # generate a wrapper

        # need to be careful about the imports. seems all the functions have the same scope, we pick the one
        # that is following the constructor
        dips = get_dpi_functions(cls)
        if len(dips) == 0:
            raise SyntaxError("Class {0} does not have any function to export to SystemVerilog".format(cls.__name__))
        else:
            imports = dips[0].func_def.imports.copy()

        func_def = DPIFunction(return_type=DataType.Void)
        func_def.imports = imports
        func_def.parent_class = cls
        call = func_def(ctor)
        func_def.arg_types[func_def.arg_names[0]] = DataType.CHandle

        cls.__init__ = call

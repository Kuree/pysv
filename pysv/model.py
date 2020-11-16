import inspect
import astor
import ast
import textwrap
from .function import dpi, DPIFunctionCall
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
        assert len(signature.parameters) == 1, "Class __init__ needs to have @dpi decorator"

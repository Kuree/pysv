import inspect
from .function import DPIFunctionCall, DPIFunction
from .types import DataType
from .util import is_class


def get_dpi_functions(cls: type):
    attrs = [getattr(cls, a) for a in dir(cls)]
    result = []
    for attr in attrs:
        if isinstance(attr, DPIFunctionCall):
            result.append(attr)
            # set init as well
            if attr == cls.__init__:
                # return type is c_handle
                attr.func_def.return_type = DataType.Object
            else:
                # normal function call
                # set the first argument to be chandle
                attr.func_def.arg_types[attr.func_def.arg_names[0]] = DataType.Object
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
        func_def.arg_types[func_def.arg_names[0]] = DataType.Object

        cls.__init__ = call


def check_class_method(cls: type):
    func_defs = get_dpi_functions(cls)
    for func_def in func_defs:
        assert func_def.func_def.base_name[0] != "_", "Protected/Private methods not allowed to " \
                                                      "be exported to SystemVerilog"


def inject_destructor(cls: type):
    assert is_class(cls)
    # use keyword "destroy" as the destructor function name

    def destroy(self):
        # empty destructor since we're going to replace it with
        pass

    if hasattr(cls, "destroy"):
        attr = getattr(cls, "destroy")
        if not isinstance(attr, DPIFunctionCall):
            raise SyntaxError('Class exported SystemVerilog cannot have a method'
                              ' called "destroy" since it is reserved for destructor')

    func_def = DPIFunction(return_type=DataType.Void)
    func_def.imports = {}
    func_def.parent_class = cls
    call = func_def(destroy)
    func_def.arg_types[func_def.arg_names[0]] = DataType.Object

    setattr(cls, "destroy", call)

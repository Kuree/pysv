import inspect
import types
import textwrap
import ast
import astor
from typing import Dict, List
from .types import DataType
from .frame import _inspect_frame


# by default we will not run the function that's wrapped in
# to test the python model functionality
# this needs to be turned on
def set_run_function(flag: bool):
    DPIFunctionCall.RUN_FUNCTION = flag


def is_run_function_set():
    return DPIFunctionCall.RUN_FUNCTION


class DPIFunction:

    def __init__(self, return_type: DataType = DataType.Int, **arg_types):
        self.return_type = return_type
        assert isinstance(self.return_type, DataType), "Return type has to be of " + DataType.__name__
        self.imports = _inspect_frame()

        self.func = None
        self.__func_name = ""

        # check arg types
        for t in arg_types.values():
            assert isinstance(t, DataType)
        self.arg_types = arg_types
        for t in self.arg_types.values():
            assert isinstance(t, DataType)
            assert t != DataType.Void, str(DataType.Void) + " can only used as return type"
        self.arg_names: List[str] = []

        self.parent_class = None

    def __call__(self, fn):
        self.func = fn
        # get it's argument definition, if it is missing, we will assume it is
        # Int type
        signature = inspect.signature(fn)
        params = signature.parameters
        for name in params:
            # currently default value not supported
            if name not in self.arg_types:
                self.arg_types[name] = DataType.Int
            # arg ordering
            self.arg_names.append(name)
        self.__func_name = fn.__name__

        return DPIFunctionCall(self)

    def get_func_src(self):
        # get the content of the function as str
        assert self.func is not None
        fn_src = inspect.getsource(self.func)
        func_tree = ast.parse(textwrap.dedent(fn_src))
        fn_body = func_tree.body[0]
        # only support one decorator
        assert len(fn_body.decorator_list) == 1, "Only dpi decorator is supported"
        # remove the decorator
        fn_body.decorator_list = []
        src = astor.to_source(fn_body)
        return src

    @property
    def func_name(self):
        if self.parent_class is None:
            return self.__func_name
        else:
            cls_name = self.parent_class.__name__
            return "{0}_{1}".format(cls_name, self.__func_name)


# aliasing
dpi = DPIFunction


class DPIFunctionCall:
    RUN_FUNCTION = False

    def __init__(self, func_def: DPIFunction):
        assert isinstance(func_def, DPIFunction)
        self.func_def = func_def
        self.args = []

    def __call__(self, *args):
        self.args = args
        if DPIFunctionCall.RUN_FUNCTION:
            return self.func_def.func(*args)
        else:
            return self

import inspect
import abc
from typing import Dict, List, Union
from .types import DataType
from .frame import _inspect_frame
from .pyast import get_function_src, get_class_src


# by default we will not run the function that's wrapped in
# to test the python model functionality
# this needs to be turned on
def set_run_function(flag: bool):
    DPIFunctionCall.RUN_FUNCTION = flag


def is_run_function_set():
    return DPIFunctionCall.RUN_FUNCTION


class Function:
    def __init__(self):
        self.imports: Dict[str, str] = {}
        self.__func_name = ""
        self.arg_names: List[str] = []
        self.arg_types: Dict[str, DataType] = {}
        self.return_type = DataType.Void
        self.parent_class: Union[type, None] = None

        # only used for init function
        self.is_init = False

    @abc.abstractmethod
    def get_func_src(self):
        pass

    @property
    @abc.abstractmethod
    def func_name(self):
        return ""

    @property
    @abc.abstractmethod
    def base_name(self):
        return ""


class DPIFunction(Function):
    def __init__(self, return_type: DataType = DataType.Int, **arg_types):
        super().__init__()
        self.return_type = return_type
        assert isinstance(self.return_type, DataType), "Return type has to be of " + DataType.__name__
        self.imports = _inspect_frame()

        self.func = None

        # check arg types
        for t in arg_types.values():
            assert isinstance(t, DataType)
        self.arg_types = arg_types
        for t in self.arg_types.values():
            assert isinstance(t, DataType)
            assert t != DataType.Void, str(DataType.Void) + " can only used as return type"

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
        # notice that for __init__, the entire class has to be generated
        if self.parent_class is not None and self.is_init:
            return get_class_src(self.parent_class)
        else:
            return get_function_src(self.func)

    @property
    def func_name(self):
        if self.parent_class is None:
            return self.__func_name
        else:
            cls_name = self.parent_class.__name__
            return "{0}_{1}".format(cls_name, self.__func_name)

    @property
    def base_name(self):
        return self.__func_name


# aliasing
sv = DPIFunction


class DPIFunctionCall:
    # all the functions will be run by default
    # Python-based hardware generator needs to turn this off
    RUN_FUNCTION = True

    def __init__(self, func_def: DPIFunction):
        # no type hints for func_def since we need to duck type it
        # due to python importing order we don't want to introduce circular import here
        self.func_def: DPIFunction = func_def
        self.args = []

    def __get__(self, instance, owner):
        # see SO answer here: https://stackoverflow.com/a/48491028
        self.func_def.parent_class = owner
        return self

    def __call__(self, *args):
        self.args = args
        if DPIFunctionCall.RUN_FUNCTION:
            # need to be extra careful about class methods
            if self.func_def.parent_class is not None:
                return self.func_def.func(self.func_def.parent_class, *args)
            else:
                return self.func_def.func(*args)
        else:
            return self

    @property
    def func_name(self):
        return self.func_def.func_name

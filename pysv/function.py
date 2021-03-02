import inspect
import abc
from typing import Dict, List, Union, Callable
from .types import DataType, Reference
from .frame import _inspect_frame, _get_import_name
from .pyast import get_function_src, get_class_src, has_return


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
        self.output_names: List[str] = []
        self.arg_types: Dict[str, DataType] = {}
        self.return_type = DataType.Void
        self.parent_class: Union[type, None] = None

        # only used for init function
        self.is_init = False

        # for class reference in args and return type
        self.arg_obj_ref = {}
        self.return_obj_ref = None

    @abc.abstractmethod
    def get_func_src(self, check_sv_decorator=True):
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
    def __init__(self, return_type: Union[DataType, type, Reference] = DataType.Int, imports=None, **arg_types):
        super().__init__()
        self.func = None
        if not isinstance(return_type, DataType) and not isinstance(return_type, type) and not isinstance(return_type,
                                                                                                          Reference):
            # someone didn't use preferred (). luckily we still support it
            assert hasattr(return_type, "__name__"), "Function does not have __name__"
            self.__call__(return_type)
        else:
            self.return_type = self.__check_arg_type("", return_type)
            # compute output names
            if isinstance(return_type, Reference):
                for arg_name, arg_type in return_type.kwargs.items():
                    assert isinstance(arg_type, DataType) and arg_type not in {DataType.Void, DataType.Object}
                    self.output_names.append(arg_name)
                    self.arg_types[arg_name] = arg_type
            assert isinstance(self.return_type, DataType), "Return type has to be of " + DataType.__name__
        if imports is None:
            self.imports = _inspect_frame()
        else:
            self.imports = {}
            for name, val in imports.items():
                val_name = _get_import_name(val, False)
                assert val_name is not None, "Unable to import {0}".format(val)
                self.imports[name] = val_name

        # check arg types
        for t in arg_types.values():
            assert isinstance(t, (DataType, type))
        for name, t in arg_types.items():
            t = self.__check_arg_type(name, t)
            assert name not in self.arg_types, "Invalid arg name " + name
            self.arg_types[name] = t
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
        if fn.__name__ == "__init__":
            # Verilator doesn't like double underscore
            # need to rename it
            self.__func_name = self.init_function_name()
            self.is_init = True
        else:
            self.__func_name = fn.__name__

        # detect return
        if self.return_type == DataType.Int and not has_return(fn):
            self.return_type = DataType.Void

        return DPIFunctionCall(self)

    def __check_arg_type(self, arg_name, arg_type):
        if isinstance(arg_type, type):
            if arg_name:
                self.arg_obj_ref[arg_name] = arg_type
            else:
                self.return_obj_ref = arg_type
            arg_type = DataType.Object
        elif isinstance(arg_type, Reference):
            arg_type = DataType.Void
            assert len(arg_name) == 0
            self.return_obj_ref = None

        return arg_type

    def get_func_src(self, check_sv_decorator: bool = True):
        # get the content of the function as str
        assert self.func is not None
        # notice that for __init__, the entire class has to be generated
        if self.parent_class is not None and self.is_init:
            return get_class_src(self.parent_class)
        else:
            return get_function_src(self.func, check_decorator=check_sv_decorator)

    def has_obj_ref(self):
        return len(self.arg_obj_ref) > 0 or self.return_obj_ref is not None

    @property
    def func_name(self):
        if self.parent_class is None:
            if self.has_obj_ref():
                return "{0}_".format(self.__func_name)
            else:
                return self.__func_name
        else:
            cls_name = self.parent_class.__name__
            return "{0}_{1}".format(cls_name, self.__func_name)

    @property
    def base_name(self):
        return self.__func_name

    @staticmethod
    def init_function_name():
        return "pysv_init"


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

        # used by third-party libraries to store information temporarily. will not be touched
        # by pysv
        self.meta = None

    def __get__(self, instance, owner):
        # see SO answer here: https://stackoverflow.com/a/48491028
        if self.func_def.parent_class is not None:
            assert self.func_def.parent_class == owner
        else:
            self.func_def.parent_class = owner
        return self

    def __call__(self, *args, **kwargs):
        if DPIFunctionCall.RUN_FUNCTION:
            # need to be extra careful about class methods
            if self.func_def.parent_class is not None:
                return self.func_def.func(self.func_def.parent_class, *args, **kwargs)
            else:
                return self.func_def.func(*args, **kwargs)
        else:
            return make_call(self, *args, **kwargs)

    def make_call(self, *args, **kwargs):
        return make_call(self, *args, **kwargs)

    @property
    def func_name(self):
        return self.func_def.func_name

    def __hash__(self):
        return hash(self.func_def.func)

    def __eq__(self, other):
        return isinstance(other, DPIFunctionCall) and self.func_def.func == other.func_def.func


class DPIFunctionCallInstance:
    def __init__(self, func_call: DPIFunctionCall, *args, **kwargs):
        self.func_call = func_call
        self.args = args
        self.kwargs = kwargs

    def str(self, is_sv: bool = True, arg_to_str: Callable = lambda x: str(x), class_var_name=None, use_ptr=False):
        """Return function call and proper ordering. notice that if it is a class method
        call, you need to specify class_var_name and use_ptr.
        """
        func_def = self.func_call.func_def
        if func_def.is_init:
            if is_sv:
                func_name = "new"
            else:
                func_name = func_def.parent_class.__name__
        else:
            if func_def.parent_class is None:
                func_name = func_def.func_name
            else:
                func_name = func_def.base_name
        # need to sort out the org ordering
        args = []
        idx = 0
        arg_names = func_def.arg_names
        if func_def.parent_class is not None:
            # this is a class method call
            arg_names = arg_names[1:]
        for arg_name in arg_names:
            if arg_name not in self.kwargs:
                assert idx < len(self.args), "Invalid function call"
                args.append(self.args[idx])
                idx += 1
            else:
                args.append(self.kwargs[arg_name])
        # need to transform them into string
        arg_values = [str(arg_to_str(arg)) for arg in args]
        arg_str = ", ".join(arg_values)
        result = "{0}({1})".format(func_name, arg_str)
        if func_def.parent_class is not None and class_var_name is not None:
            if not is_sv and use_ptr:
                dot = "->"
            else:
                dot = "."
            result = "{0}{1}{2}".format(class_var_name, dot, result)
        if not is_sv and use_ptr and func_def.is_init:
            # create new. users are free to wrap it with smart pointers
            result = "new " + result
        return result


def make_call(func, *args, **kwargs):
    # avoid circular import
    import pysv.model
    if type(func) == type:
        pysv.model.check_class_ctor(func)
        func = func.__init__

    result = DPIFunctionCallInstance(func, *args, **kwargs)
    return result

import inspect
import gc
from .function import dpi, DPIFunctionCall
from .types import DataType
from .frame import _inspect_frame


class PySVModel:
    def __init__(self):
        # need to figure out the args and arg names
        self.imports = _inspect_frame()
        frame = inspect.currentframe().f_back
        signatures = inspect.signature(gc.get_referrers(frame.f_code)[0])
        local_vars = frame.f_locals
        # decide types here
        self.arg_names = []
        self.arg_types = {}
        for idx, arg_name in enumerate(signatures.parameters):
            arg = local_vars[arg_name]
            if idx == 0:
                assert isinstance(arg, PySVModel)
                # drop the "self" since we don't have that in C DPI interface
                continue
            if isinstance(arg, str):
                t = DataType.String
            elif isinstance(arg, int):
                t = DataType.Int
            elif isinstance(arg, object):
                t = DataType.CHandle
            else:
                raise ValueError("Unable to convert {0}({1}) to C types".format(arg_name, arg))
            self.arg_names.append(arg_name)
            self.arg_types[arg_name] = t

        # hardcode the func name
        self.func_name = self.__class__.__name__ + "__init__"

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, name)
        if isinstance(obj, DPIFunctionCall):
            func_def = obj.func_def
            if func_def.parent_class is not None:
                assert func_def.parent_class == self.__class__
            else:
                func_def.parent_class = self.__class__
        return obj

    @dpi(return_type=DataType.Void)
    def destroy(self):
        # actual implementation provided by the codegen
        pass

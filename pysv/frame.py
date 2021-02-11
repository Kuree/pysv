import inspect
import types
import sys
from typing import Dict

__EXCLUDE_MODULE_NAME = {"__builtins__", "@py_builtins", "@pytest_ar", "pytest", "pysv", "importlib"}
__ADDITIONAL_EXCLUDE_NAME = set()


def __should_exclude(name):
    return name in __EXCLUDE_MODULE_NAME or name in __ADDITIONAL_EXCLUDE_NAME


def _inspect_frame(num_frame=2) -> Dict[str, str]:
    # need to found out at this level what are the all imported modules
    # need to inspect one frame earlier
    # although it has some performance issue, it will only be called when a new type of DPI function
    # is registered
    frame = inspect.currentframe()
    for _ in range(num_frame):
        frame = frame.f_back
    visible_vars = frame.f_globals.copy()
    local_vars = frame.f_locals
    # local can override global variables
    visible_vars.update(local_vars)
    imports: Dict[str, str] = {}
    for name, val in visible_vars.items():
        full_name = None
        if isinstance(val, types.ModuleType):
            if name not in __EXCLUDE_MODULE_NAME:
                full_name = _get_import_name(val)
        else:
            full_name = _get_import_name(val)
        if full_name is not None:
            imports[name] = full_name
    return imports


def _get_import_name(val, check_type=True):
    if isinstance(val, types.ModuleType):
        return val.__name__
    else:
        # we support class type import as well
        if not getattr(val, "__module__", None):
            return None
        module_name = val.__module__.split(".")[0]
        full_name = None
        if check_type and __should_exclude(module_name):
            # don't care about excluded names
            return None
        if isinstance(val, type):
            full_name = "{0}.{1}".format(val.__module__, val.__qualname__)
        elif callable(val):
            module_name = val.__module__.split(".")[0]
            if check_type and (__should_exclude(module_name) or module_name.startswith("test_")):
                # don't care about excluded names
                # also if the module name starts with "test_"
                return None
            if hasattr(val, "__name__"):
                full_name = "{0}.{1}".format(val.__module__, val.__name__)
        if full_name is None or (check_type and module_name == "__main__" or "<locals>" in full_name):
            return None
        return full_name


def add_exclude_module_name(name):
    __ADDITIONAL_EXCLUDE_NAME.add(name)


def clear_exclude_module_name():
    __ADDITIONAL_EXCLUDE_NAME.clear()

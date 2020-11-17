import inspect
import types
from typing import Dict

__EXCLUDE_MODULE_NAME = {"__builtins__", "@py_builtins", "@pytest_ar", "pytest", "pysv"}


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
        if isinstance(val, types.ModuleType) and name not in __EXCLUDE_MODULE_NAME:
            imports[name] = val.__name__
    return imports

import sys


def should_add_class(func_defs):
    for func_def in func_defs:
        if type(func_def) == type:
            return True
    return False


def should_add_sys_path(func_defs):
    # looking into the imported module and see if they are system module
    defs = []
    for func_def in func_defs:
        if type(func_def) == type:
            # just need to get the constructor
            defs.append(func_def.__init__)
        else:
            defs.append(func_def)
    built_in_modules = sys.builtin_module_names
    for func_def in defs:
        for module_name in func_def.imports.values():
            if module_name not in built_in_modules:
                return True
    return False

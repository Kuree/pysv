def should_add_class(func_defs):
    result = False
    for func_def in func_defs:
        if type(func_def) == type:
            return True
    return result

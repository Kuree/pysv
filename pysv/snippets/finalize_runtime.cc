    // clear the cached global imports
    global_imports.reset();
    // clear the object map
    py_obj_map.reset();
    // the last part is tear down the runtime
    guard.reset();
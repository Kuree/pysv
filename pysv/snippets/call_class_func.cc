py::object call_class_func(void *py_ptr, const char *func_name) {
    if (py_obj_map.find(py_ptr) == py_obj_map.end()) {
        std::cerr << "ERROR: unable to call function " << func_name << std::endl;
        return py::none;
    }
    auto handle = py_obj_map.at(py_ptr);
    auto func = handle.attr(func_name);
    auto result = func();
    return result;
}
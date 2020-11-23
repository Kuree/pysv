template<class ...Args>
py::object call_class_func(void *py_ptr, const std::string &func_name, Args &&...args) {
    if (!py_obj_map) return py::none();
    if (py_obj_map->find(py_ptr) == py_obj_map->end()) {
        std::cerr << "ERROR: unable to call function " << func_name
                  << " from ptr " << py_ptr << std::endl;
        return py::none();
    }
    auto handle = py_obj_map->at(py_ptr);

    // special case for __destroy__ call
    if (func_name == "destroy") {
        // this is a special case
        // 1. manually decrease the reference we increased during object creation
        handle.dec_ref();
        // 2. use pybind's RAII to remove the actual reference
        py_obj_map->erase(py_ptr);
        return py::none();
    }

    auto func = handle.attr(func_name.c_str());
    auto result = func(args...);
    return result;
}

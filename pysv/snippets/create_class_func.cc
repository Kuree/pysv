void * create_class_func(py::dict &locals) {
    if (!py_obj_map) {
        py_obj_map = std::unique_ptr<std::unordered_map<void*, py::object>>(new std::unordered_map<void*, py::object>());
    }
    py::object result = locals["__result"];
    // manually increase the ref count to avoid being gc'ed; just in case
    result.inc_ref();
    auto r_ptr = result.ptr();
    py_obj_map->emplace(r_ptr, result);
    return r_ptr;
}
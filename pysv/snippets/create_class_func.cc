void * create_class_func(py::dict &locals, const std::string &class_name) {
    if (!py_obj_map) {
        py_obj_map = std::unique_ptr<std::unordered_map<void*, py::object>>(new std::unordered_map<void*, py::object>());
    }
    py::object result = locals["__result"];
    // manually increase the ref count to avoid being gc'ed; just in case
    result.inc_ref();
    auto r_ptr = result.ptr();
    py_obj_map->emplace(r_ptr, result);
    // also need to taken care of move the class definition to
    if (!class_name.empty()) {
        if (!class_defs) {
            class_defs = std::unique_ptr<py::dict>(new py::dict());
        }
        (*class_defs)[class_name.c_str()] = locals[class_name.c_str()];
    }
    return r_ptr;
}
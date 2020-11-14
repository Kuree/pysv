void * create_class_func(py::dict &locals) {
    py::object result = locals["__result"]
    // manually increase the ref count to avoid being gc'ed; just in case
    result.inc_ref();
    auto r_ptr = result.ptr();
    py_obj_map.emplace(r_ptr, result);
    return r_ptr;
}
void get_local_object(const std::string &local_name, void *ptr, py::dict &locals) {
    if (!py_obj_map || py_obj_map->find(ptr) == py_obj_map->end()) {
        std::cerr << "Unable to find object for " << local_name << std::endl;
        return;
    }
    auto obj = py_obj_map->at(ptr);
    locals[local_name.c_str()] = obj;
}
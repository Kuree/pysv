void import_module(const std::string &module_name, const std::string &imported_name,
                   py::dict &globals) {
    if (!global_imports) {
        global_imports = std::unique_ptr<std::unordered_map<std::string, py::object>>(new std::unordered_map<std::string, py::object>());
    }
    if (global_imports->find(module_name) == global_imports->end()) {
        auto m = py::module::import(module_name.c_str());
        global_imports->emplace(module_name, m);
    }
    auto &m = global_imports->at(module_name);
    globals[imported_name.c_str()] = m;
}
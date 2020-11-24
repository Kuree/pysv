namespace py = pybind11;
std::unique_ptr<std::unordered_map<std::string, py::object>> global_imports = nullptr;
std::unique_ptr<py::scoped_interpreter> guard = nullptr;
std::unique_ptr<std::unordered_map<void*, py::object>> py_obj_map;
std::unique_ptr<py::dict> class_defs;
std::string string_result_value;

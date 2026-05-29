std::string get_env(const char *name) {
    std::string result;
#ifdef _WIN32
    char *path_var = nullptr;
    size_t len = 0;
    auto err = _dupenv_s(&path_var, &len, name);
    if (!err && path_var) {
        result = std::string(path_var);
        free(path_var);
    }
#else
    auto r = std::getenv(name);
    if (r) {
        result = r;
    }
#endif
    return result;
}

void unset_env(const char *name) {
#ifdef _WIN32
    _putenv_s(name, "");
#else
    unsetenv(name);
#endif
}

std::pair<std::string, std::string> get_py_env() {
    std::string python_home = get_env("PYTHONHOME");
    std::string python_path = get_env("PYTHONPATH");
    return std::make_pair(python_home, python_path);
}

void unset_py_env() {
    unset_env("PYTHONHOME");
    unset_env("PYTHONPATH");
}

void set_env(const char *name, const std::string &value) {
    if (value.empty()) {
        unset_env(name);
        return;
    }
#ifdef _WIN32
    _putenv_s(name, value.c_str());
#else
    setenv(name, value.c_str(), 1);
#endif
}

void set_py_env(const std::pair<std::string, std::string> &values) {
    set_env("PYTHONHOME", values.first);
    set_env("PYTHONPATH", values.second);
}

static bool has_py_env_set = false;
void initialize_guard() {
    if (guard) return;
    // make sure if PYTHONHOME and PYTHONPATH are set or not
    auto python_env_vars = get_py_env();
    bool has_python_env_vars = !python_env_vars.first.empty() || !python_env_vars.second.empty();

    if (has_python_env_vars || !conda_python_home.empty()) {
        // Simulator launchers such as Vivado may set PYTHONHOME/PYTHONPATH to
        // their bundled Python. Temporarily replace those with the build-time
        // interpreter paths before pybind11 initializes CPython.
        unset_py_env();
        if (!conda_python_home.empty()) {
            set_py_env(std::make_pair(conda_python_home, conda_python_path));
        }
        guard = std::unique_ptr<py::scoped_interpreter>(new py::scoped_interpreter());
        unset_py_env();
        if (has_python_env_vars) {
            set_py_env(python_env_vars);
            has_py_env_set = true;
        }
    } else {
        guard = std::unique_ptr<py::scoped_interpreter>(new py::scoped_interpreter());
    }
}

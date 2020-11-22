std::vector<std::string> get_tokens(const std::string &line, const std::string &delimiter) {
    std::vector<std::string> tokens;
    size_t prev = 0, pos = 0;
    std::string token;
    // copied from https://stackoverflow.com/a/7621814
    while ((pos = line.find_first_of(delimiter, prev)) != std::string::npos) {
        if (pos > prev) {
            tokens.emplace_back(line.substr(prev, pos - prev));
        }
        prev = pos + 1;
    }
    if (prev < line.length()) tokens.emplace_back(line.substr(prev, std::string::npos));
    // remove empty ones
    std::vector<std::string> result;
    result.reserve(tokens.size());
    for (auto const &t : tokens)
        if (!t.empty()) result.emplace_back(t);
    return result;
}

void import_module(const std::string &module_name, const std::string &imported_name,
                   py::dict &globals) {
    if (!global_imports) {
        global_imports = std::unique_ptr<std::unordered_map<std::string, py::object>>(new std::unordered_map<std::string, py::object>());
    }
    if (global_imports->find(module_name) == global_imports->end()) {
        py::object target;
        // tokenize the module name in case it has nested namespace
        bool top_module = true;
        auto name_tokens = get_tokens(module_name, ".");
        for (auto const &name: name_tokens) {
            if (top_module) {
                target = py::module::import(name.c_str());
                top_module = false;
            } else {
                target = target.attr(name.c_str());
            }
        }
        global_imports->emplace(module_name, target);
    }
    auto &m = global_imports->at(module_name);
    globals[imported_name.c_str()] = m;
}
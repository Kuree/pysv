void load_class_defs(py::dict &globals) {
    if (class_defs) {
        for (auto const &iter: (*class_defs)) {
            globals[iter.first] = iter.second;
        }
    }
}
void check_sys_path() {
    // only modify the sys.path if the one is . (set by pybind)
    auto sys = py::module::import("sys");
    auto sys_path = sys.attr("path");
    auto last_path_len = py::len(sys.attr("path").attr("__getitem__")(py::int_(-1)));
    if (last_path_len == 1) {
        // need to set the path
        // clear first
        sys.attr("path").attr("clear")();
        for (auto const path: SYS_PATH) {
            sys.attr("path").attr("append")(py::str(path));
        }
    }
}
void check_interpreter() {
    if (!guard) guard = std::unique_ptr<py::scoped_interpreter>(new py::scoped_interpreter());
}
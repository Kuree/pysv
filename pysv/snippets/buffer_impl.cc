#include "svdpi.h"

py::memoryview to_buffer(const svOpenArrayHandle array_handle) {
    ssize_t element_size = sizeof(int32_t);
    void *base_ptr = nullptr;
    std::vector<ssize_t> sizes = {};
    std::vector<ssize_t> strides = {};

    // we try to query the underlying representation
    base_ptr = svGetArrayPtr(array_handle);
    if (!base_ptr) {
        throw std::runtime_error("Array type does not have native C representation");
    }
    auto dim = svDimensions(array_handle);
    for (auto i = 0; i < dim; i++) {
        auto s = svSize(array_handle, i);
        sizes.emplace_back(s);
    }
    // assumes row major ordering
    ssize_t stride = element_size;
    strides = std::vector<ssize_t>(dim, element_size);
    for (int i = 0; i < dim - 1; i++) {
        stride *= sizes[i];
        strides[i] = stride;
    }

    return py::memoryview::from_buffer(
        base_ptr,                                 /* Pointer to buffer */
        element_size,                             /* Size of one scalar */
        py::format_descriptor<int32_t>::value, /* Python struct-style format descriptor */
        sizes,                                    /* Buffer dimensions */
        strides                                   /* Strides (in bytes) for each index */
    );
}

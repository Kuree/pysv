#include "pybind11/include/pybind11/embed.h"
#include "pybind11/include/pybind11/eval.h"
#include <iostream>
#include <unordered_map>
#include <memory>

// used for ModelSim/Questa to resolve some runtime native library loading issues
// not needed for Xcelium and vcs, but include just in case
#ifdef __linux__
#include <dlfcn.h>
#endif
namespace py = pybind11;
py::scoped_interpreter guard;
std::string string_result_value;

extern "C" {
__attribute__((visibility("default"))) int32_t simple_func(int32_t a,
                                                           int32_t b,
                                                           int32_t c) {
  auto globals = py::dict();

  auto locals = py::dict();
  locals["__a"] = a;
  locals["__b"] = b;
  locals["__c"] = c;

  py::exec(R"(
def simple_func(a, b, c):
    return a + b - c

__result = simple_func(__a, __b, __c)
)", globals, locals);
  return locals["__result"].cast<int32_t>();
}
}

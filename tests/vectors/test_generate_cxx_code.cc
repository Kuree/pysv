#include "pybind11/include/pybind11/embed.h"
#include "pybind11/include/pybind11/eval.h"
namespace py = pybind11;
py::scoped_interpreter guard;
std::string string_result_value;

extern "C" {
__attribute__((visibility("default"))) int32_t simple_func(int32_t a,
                                                           int32_t b,
                                                           int32_t c) {
  auto locals = py::dict();
  locals["__a"] = a;
  locals["__b"] = b;
  locals["__c"] = c;

  py::exec(R"(
def simple_func(a, b, c):
    return a + b - c

__result = simple_func(__a, __b, __c)
)", py::globals(), locals);
  return locals["__result"].cast<int32_t>();
}
}

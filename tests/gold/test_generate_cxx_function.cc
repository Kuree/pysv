__attribute__((visibility("default"))) int32_t simple_func(int32_t a,
                                                           int32_t b,
                                                           int32_t c) {
  check_interpreter();
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

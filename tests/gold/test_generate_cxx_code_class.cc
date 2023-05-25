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
std::unique_ptr<std::unordered_map<std::string, py::object>> global_imports = nullptr;
std::unique_ptr<py::scoped_interpreter> guard = nullptr;
std::unique_ptr<std::unordered_map<void*, py::object>> py_obj_map;
std::unique_ptr<py::dict> class_defs;
std::string string_result_value;

void check_interpreter() {
    if (!guard) guard = std::unique_ptr<py::scoped_interpreter>(new py::scoped_interpreter());
}
template<class ...Args>
py::object call_class_func(void *py_ptr, const std::string &func_name, Args &&...args) {
    if (!py_obj_map) return py::none();
    if (py_obj_map->find(py_ptr) == py_obj_map->end()) {
        std::cerr << "ERROR: unable to call function " << func_name
                  << " from ptr " << py_ptr << std::endl;
        return py::none();
    }
    auto handle = py_obj_map->at(py_ptr);

    // special case for __destroy__ call
    if (func_name == "destroy") {
        // this is a special case
        // 1. manually decrease the reference we increased during object creation
        handle.dec_ref();
        // 2. use pybind's RAII to remove the actual reference
        py_obj_map->erase(py_ptr);
        return py::none();
    }

    auto func = handle.attr(func_name.c_str());
    auto result = func(args...);
    return result;
}

void * create_class_func(py::dict &locals, const std::string &class_name) {
    if (!py_obj_map) {
        py_obj_map = std::unique_ptr<std::unordered_map<void*, py::object>>(new std::unordered_map<void*, py::object>());
    }
    py::object result = locals["__result"];
    // manually increase the ref count to avoid being gc'ed; just in case
    result.inc_ref();
    auto r_ptr = result.ptr();
    py_obj_map->emplace(r_ptr, result);
    // also need to taken care of move the class definition to
    if (!class_name.empty()) {
        if (!class_defs) {
            class_defs = std::unique_ptr<py::dict>(new py::dict());
        }
        (*class_defs)[class_name.c_str()] = locals[class_name.c_str()];
    }
    return r_ptr;
}
void load_class_defs(py::dict &globals) {
    if (class_defs) {
        for (auto const &iter: (*class_defs)) {
            globals[iter.first] = iter.second;
        }
    }
}

extern "C" {
__attribute__((visibility("default"))) void* SomeClass_pysv_init() {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();

  py::exec(R"(
class SomeClass:

    def __init__(self):
        self.value = 'hello world\n'

    def print_a(self):
        print(self.value)

    def print_b(self, num):
        print(self.value * num)

    def plus(self, num):
        return num + 1

    def add_sub(self, a, b):
        return a + b, a - b

__result = SomeClass()
)", globals, locals);
  return create_class_func(locals, "SomeClass");
}

__attribute__((visibility("default"))) void SomeClass_add_sub(void* self,
                                                              uint32_t a,
                                                              uint32_t b,
                                                              uint32_t *res_add,
                                                              uint32_t *res_sub) {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();
  locals["__self"] = self;
  locals["__a"] = a;
  locals["__b"] = b;

  locals["__result"] = call_class_func(self,
                                       "add_sub",
                                       locals["__a"],
                                       locals["__b"]);
  auto ref_result = locals["__result"].cast<py::list>();
  if (py::len(ref_result) != 2) {
    throw std::runtime_error("Invalid return tuple size");
  }
  *res_add = ref_result[0].cast<uint32_t>();
  *res_sub = ref_result[1].cast<uint32_t>();
}

__attribute__((visibility("default"))) void SomeClass_destroy(void* self) {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();
  locals["__self"] = self;

  locals["__result"] = call_class_func(self,
                                       "destroy");
}

__attribute__((visibility("default"))) int32_t SomeClass_plus(void* self,
                                                              int32_t num) {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();
  locals["__self"] = self;
  locals["__num"] = num;

  locals["__result"] = call_class_func(self,
                                       "plus",
                                       locals["__num"]);
  return locals["__result"].cast<int32_t>();
}

__attribute__((visibility("default"))) void SomeClass_print_a(void* self) {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();
  locals["__self"] = self;

  locals["__result"] = call_class_func(self,
                                       "print_a");
}

__attribute__((visibility("default"))) void SomeClass_print_b(void* self,
                                                              int32_t num) {
  check_interpreter();
  auto globals = py::dict();
  load_class_defs(globals);
  auto locals = py::dict();
  locals["__self"] = self;
  locals["__num"] = num;

  locals["__result"] = call_class_func(self,
                                       "print_b",
                                       locals["__num"]);
}
__attribute__((visibility("default"))) void pysv_finalize() {
    // clear the cached global imports
    global_imports.reset();
    // clear the object map
    py_obj_map.reset();
    // clear the class map
    class_defs.reset();
    // the last part is tear down the runtime
    guard.reset();
}
}
#ifndef PYSV_CXX_BINDING
#define PYSV_CXX_BINDING
namespace pysv {
class PySVObject {
public:
  PySVObject() = default;
  PySVObject(void* ptr): pysv_ptr(ptr) {}
  PySVObject(const PySVObject &obj) : pysv_ptr(obj.pysv_ptr) {}
  virtual ~PySVObject() = default;

  void *pysv_ptr = nullptr;
};
class SomeClass : public PySVObject {
public:
  __attribute__((visibility("default")))  SomeClass();
  __attribute__((visibility("default"))) void add_sub(uint32_t a,
                                                      uint32_t b,
                                                      uint32_t *res_add,
                                                      uint32_t *res_sub);
  __attribute__((visibility("default")))  ~SomeClass() override;
  __attribute__((visibility("default"))) int32_t plus(int32_t num);
  __attribute__((visibility("default"))) void print_a();
  __attribute__((visibility("default"))) void print_b(int32_t num);
};
SomeClass::SomeClass() {
    pysv_ptr = SomeClass_pysv_init();
}
void SomeClass::add_sub(uint32_t a,
          uint32_t b,
          uint32_t *res_add,
          uint32_t *res_sub) {
    SomeClass_add_sub(pysv_ptr, a, b, res_add, res_sub);
}
SomeClass::~SomeClass() {
    SomeClass_destroy(pysv_ptr);
}
int32_t SomeClass::plus(int32_t num) {
    return SomeClass_plus(pysv_ptr, num);
}
void SomeClass::print_a() {
    SomeClass_print_a(pysv_ptr);
}
void SomeClass::print_b(int32_t num) {
    SomeClass_print_b(pysv_ptr, num);
}
}
#endif // PYSV_CXX_BINDING

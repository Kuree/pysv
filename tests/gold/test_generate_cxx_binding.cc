#ifndef PYSV_CXX_BINDING
#define PYSV_CXX_BINDING
#include <iostream>
extern "C" {
void* SomeClass_pysv_init();
void SomeClass_add_sub(void* self,
                       uint32_t a,
                       uint32_t b,
                       uint32_t *res_add,
                       uint32_t *res_sub);
void SomeClass_destroy(void* self);
int32_t SomeClass_plus(void* self,
                       int32_t num);
void SomeClass_print_a(void* self);
void SomeClass_print_b(void* self,
                       int32_t num);
void pysv_finalize();
}
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
  SomeClass();
  void add_sub(uint32_t a,
               uint32_t b,
               uint32_t *res_add,
               uint32_t *res_sub);
  ~SomeClass() override;
  int32_t plus(int32_t num);
  void print_a();
  void print_b(int32_t num);
};
}
#endif // PYSV_CXX_BINDING

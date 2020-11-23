#ifndef PYSV_CXX_BINDING
#define PYSV_CXX_BINDING
#include <iostream>
extern "C" {
void* SomeClass_pysv_init();
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
  void *pysv_ptr = nullptr;
  virtual ~PySVObject() = default;
};
class SomeClass : public PySVObject {
public:
  SomeClass();
  ~SomeClass() override;
  int32_t plus(int32_t num);
  void print_a();
  void print_b(int32_t num);
};
}
#endif // PYSV_CXX_BINDING

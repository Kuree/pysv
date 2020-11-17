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
}
class SomeClass {
private:
  void *pysv_ptr;
public:
   SomeClass() {
    pysv_ptr = SomeClass_pysv_init();
  }
  void destroy() {
    SomeClass_destroy(pysv_ptr);
  }
  int32_t plus(int32_t num) {
    return SomeClass_plus(pysv_ptr, num);
  }
  void print_a() {
    SomeClass_print_a(pysv_ptr);
  }
  void print_b(int32_t num) {
    SomeClass_print_b(pysv_ptr, num);
  }
};
#endif // PYSV_CXX_BINDING

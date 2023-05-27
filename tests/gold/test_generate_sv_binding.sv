`ifndef PYSV_PYSV
`define PYSV_PYSV
package pysv;
import "DPI-C" function chandle SomeClass_pysv_init();
import "DPI-C" function void SomeClass_add_sub(input chandle self,
                                               input int unsigned a,
                                               input int unsigned b,
                                               output int unsigned res_add,
                                               output int unsigned res_sub);
import "DPI-C" function void SomeClass_destroy(input chandle self);
import "DPI-C" function int SomeClass_plus(input chandle self,
                                           input int num);
import "DPI-C" function void SomeClass_print_a(input chandle self);
import "DPI-C" function void SomeClass_print_b(input chandle self,
                                               input int num);
import "DPI-C" function void pysv_finalize();
class PySVObject;
chandle pysv_ptr;
endclass
class SomeClass extends PySVObject;
  function new();
    pysv_ptr = SomeClass_pysv_init();
  endfunction
  function void add_sub(input int unsigned a,
                        input int unsigned b,
                        output int unsigned res_add,
                        output int unsigned res_sub);
    SomeClass_add_sub(pysv_ptr, a, b, res_add, res_sub);
  endfunction
  function void destroy();
    SomeClass_destroy(pysv_ptr);
  endfunction
  function int plus(input int num);
    return SomeClass_plus(pysv_ptr, num);
  endfunction
  function void print_a();
    SomeClass_print_a(pysv_ptr);
  endfunction
  function void print_b(input int num);
    SomeClass_print_b(pysv_ptr, num);
  endfunction
endclass
endpackage
`endif // PYSV_PYSV

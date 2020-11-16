`ifndef PYSV_PYSV
`define PYSV_PYSV
package pysv;
import "DPI-C" function chandle SomeClass___init__();
import "DPI-C" function void SomeClass_print_a(input chandle self);
import "DPI-C" function void SomeClass_print_b(input chandle self,
                                               input int num);
class SomeClass;
  local chandle pysv_ptr;
  function new();
    pysv_ptr = SomeClass___init__();
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

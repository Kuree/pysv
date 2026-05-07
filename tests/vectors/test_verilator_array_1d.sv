`include "pysv_pkg.sv"

module test_verilator_array_1d();

import pysv::*;

int a[4:0];

initial begin
  for (int i = 0; i < 5; i++) begin
    a[i] = 2;
  end
  set_value(a);
  $display("%0d", a[3]);
end

endmodule

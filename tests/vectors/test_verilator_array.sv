`include "pysv_pkg.sv"

module test_verilator_array();

import pysv::*;

int a[3:0];

initial begin
  for (int i = 0; i < 4; i++) begin
    a[i] = 2;
  end
  set_value(a);
  $display("%0d", a[2]);
end

endmodule

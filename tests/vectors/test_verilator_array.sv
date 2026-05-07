`include "pysv_pkg.sv"

module test_verilator_array();

import pysv::*;

int a[2:0][4:0];

initial begin
  for (int i = 0; i < 3; i++) begin
    for (int j = 0; j < 5; j++) begin
      a[i][j] = 2;
    end
  end
  set_value(a);
  $display("%0d", a[0][4]);
  $display("%0d", a[1][3]);
  $display("%0d", a[2][0]);
  $display("%0d", a[2][1]);
end

endmodule

`include "pysv_pkg.sv"

module test_verilator_array();

import pysv::*;

int a[3:0][3:0];

initial begin
  for (int i = 0; i < 4; i++) begin
    for (int j = 0; j < 4; j++) begin
      a[i][j] = 2;
    end
  end
  set_value(a);
  $display("%0d", a[2][1]);
end

endmodule

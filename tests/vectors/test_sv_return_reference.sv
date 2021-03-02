module top;

import pysv::*;

logic[31:0] a, b;

initial begin
    set_value(a, b);
    assert (a == 42);
    assert (b == 43);

    pysv_finalize();
end

endmodule

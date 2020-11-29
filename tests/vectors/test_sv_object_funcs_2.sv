module top;

import pysv::*;

initial begin
    int value;
    ClassA2 a;
    a = new();
    value = add(a);
    assert (value == 42);
    pysv_finalize();
end

endmodule

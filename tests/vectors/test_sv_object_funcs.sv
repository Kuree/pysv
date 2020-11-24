module top;

import pysv::*;

ClassA a1, a2;
ClassB b;

initial begin
    int value;
    a1 = new();
    b = new(a1);
    a2 = b.create_a(21);
    value = b.add(a2);
    assert (value == 42);
    pysv_finalize();
end

endmodule

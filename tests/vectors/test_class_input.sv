module top;

import pysv::*;

ClassA a1, a2;
ClassB b;

initial begin
    int value;
    a1 = new(1);
    a2 = new(41);
    b = new(a1);
    value = b.add(a2);
    assert (value == 42);
end

endmodule

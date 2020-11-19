module top;

import pysv::simple_mat_mal, pysv::pysv_finalize;

initial begin
    int sum;
    sum = simple_mat_mal(2, 3);
    assert (sum == 2 * 3 * 4 * 2);

    pysv_finalize();
end


endmodule
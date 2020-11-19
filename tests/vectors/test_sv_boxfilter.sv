module top;

import pysv::BoxFilter, pysv::pysv_finalize;

localparam int FILTER_SIZE = 4;

logic       clk;
logic       rst;
logic[31:0] in;
logic[31:0] out;

box_filter #(FILTER_SIZE) dut (.*);
BoxFilter model;

initial clk = 0;
always #10 clk <= ~clk;

task reset();
    rst = 0;
    in = 0;
    #1;
    rst = 1;
    #1;
    rst = 0;
    #1;
endtask

initial begin
    reset();
    model = new(FILTER_SIZE);

    for (int i = 0; i < 10; i++) begin
        in = $urandom() % 'hFFFF;
        model.push(in);
        @(posedge clk);
        @(negedge clk);
        assert (out == model.avg()) else $error("expect %d, got %d", model.avg(), out);
    end

    // need to destroy the runtime
    pysv_finalize();
    $finish();
end

endmodule
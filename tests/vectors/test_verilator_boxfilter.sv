module box_filter #(
    parameter int FILTER_SIZE=4
) (
    input  logic       clk,
    input  logic       rst,
    input  logic[31:0]  in,
    output logic[31:0]  out
);

localparam PTR_SIZE = $clog2(FILTER_SIZE);

logic [FILTER_SIZE-1:0][31:0] values;
logic [PTR_SIZE-1:0] ptr;

always_ff @(posedge clk, posedge rst) begin
    if (rst) begin
        values <= 'd0;
        ptr <= 'd0;
    end
    else begin
        values[ptr] <= in;
        ptr <= PTR_SIZE'((ptr + 'd1) % FILTER_SIZE);
    end
end

always_comb begin
    logic [31:0] result = 0;
    for (int i = 0; i < FILTER_SIZE; i++) begin
        result += values[i];
    end
    out = result / FILTER_SIZE;
end

endmodule
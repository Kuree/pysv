function int echo(int a);
    return a + 1;
endfunction

module main;
initial begin
   test_lib::test();
end

endmodule
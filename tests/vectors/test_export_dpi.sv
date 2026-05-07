module main;
function int echo(int a);
    return a + 1;
endfunction

export "DPI-C" function echo;

initial begin
   test_lib::pysv_init_export_scope();
   test_lib::test();
   test_lib::pysv_finalize();
   $finish;
end

endmodule

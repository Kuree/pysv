.. _basics:

Basic usages
============
This sections demonstrates the basic features of pysv.

Hello World!
------------

Here is a simple yet complete example to execute some hello-world code from Python

.. code-block:: Python

    from pysv import sv, compile_lib, generate_sv_binding

    @sv()
    def hello_world():
        print("hello world!")

    # compile the a shared_lib into build folder
    lib_path = compile_lib([hello_world], cwd="build")
    # generate SV binding
    generate_sv_binding([hello_world], filename="pysv_pkg.sv")


Now we can use the function in our test bench:

.. code-block:: SystemVerilog


    module top;
    // import from the pysv package
    import pysv::hello_world;

    initial begin
        hello_world();
    end
    endmodule

To run it with Xcelium we can simply do

.. code-block::

    xrun pysv_pkg.sv top.sv -sv_lib build/libpysv.so

And it will print out ``helo world!``. Notice that ``build/libpysv.so`` can be obtained
from ``lib_path``.

Function arguments and return types
-----------------------------------


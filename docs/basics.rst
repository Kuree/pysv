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
By default, if a function argument type is not specified, pysv will assume it is of
``DataType.Int`` type (``int32_t`` in C).
To specify the argument type, we can add the types to the function decorator.

.. code-block:: Python

    from pysv import sv, DataType

    @sv(s=DataType.String)
    def print_dup_s(s, repeat):
        print(s * repeat)

In the example above, we specify the type of argument ``s`` to be string.
Since ``repeat`` is an integer, we leave it unspecified to use default typing.

To specify return type, simply use keyword ``return_type``, as shown below:

.. code-block:: Python

    from pysv import sv, DataType

    @sv(return_type=DataType.String)
    def get_str():
        return "Hello World"

pysv uses two rules to infer return types if not specified

1. If the function body does not have any return statement, then it's default to
``DataType.Void``.
2. Otherwise it is set to ``DataType.Int``

For more complex data type such as Python objects, please refer to :doc:`Object-Oriented Programming <advanced/oop>`.

Library compilation
-------------------
In order to use pysv in your testbench, you first need to compile the python
code into a native shared object, which can be linked into any supported simulators.
To do so, simply call the function ``compile_lib``:

.. code-block:: Python

    lib_path = compile_lib(func_defs, cwd)


``compile_lib`` returns the path to compiled shared object. ``cwd`` specifies the
working directory of staged compilation. You can re-use the same ``cwd`` if you
wish the speed up the compilation speed.

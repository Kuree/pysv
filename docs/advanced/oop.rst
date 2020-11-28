.. _oop:

Object-Oriented Programming with pysv
=====================================

pysv supports object-oriented programming. Here is a simply example on how to
use it:

.. code-block:: Python

  from pysv import sv, DataType

  class Foo:
    @sv()
    def __init__(self, num):
        self.num = num

    @sv()
    def bar(self, num):
        return self.num + num


  @sv(foo=Foo)
  def foo_bar(foo, num):
      return foo.bar(num)


  lib_path = compile_lib([Foo, foo_bar], cwd="build")


We can use the class type directly in the ``compile_lib``. pysv will inspect each methods and
export the methods decorated with ``@sv``.

.. note::

  If the class constructor does not have any argument except for ``self``, we can omit the
  ``@sv`` decorator since pysv will generate default constructor automatically. Nonetheless,
  it doesn't hurt to decorate the constructor.

To use it in the SystemVerilog, first, we generate the SystemVerilog binding

.. code-block:: Python

  from pysv import generate_sv_binding

  generate_sv_binding([Foo, foo_bar], filename="pysv_pkg.sv")

Then we can use the class directly in a test bench, as shown below:

.. code-block:: SystemVerilog

    module top;

    import pysv::*;

    initial begin
        Foo foo;
        int res;
        foo = new(41);
        res = foo_bar(foo, 1);
        assert (res == 42);
        // need to finalize the pysv runtime
        pysv_finalize();
    end

    endmodule

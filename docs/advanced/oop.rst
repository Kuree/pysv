.. _oop:

Object-Oriented Programming
===========================

pysv supports object-oriented programming. Here is a simply example on how to
use it:

.. code-block:: Python

  from pysv import sv, DataType, compile_lib

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
        // functions that takes generated class object
        res = foo_bar(foo, 1);
        assert (res == 42);
        // call class methods as well
        res = foo.bar(-40);
        assert (res == 1);
        // need to finalize the pysv runtime
        pysv_finalize();
    end

    endmodule

Save the test bench file as ``top.sv`` and we can run the example with Xcelium
with the following command:

.. code-block::

    xrun pysv_pkg.sv top.sv -sv_lib build/libpysv.so

The simulation will finish without triggering the assertion error.

We can open the generated SystemVerilog binding file to see the actual SystemVerilog
class generated:

.. code-block:: SystemVerilog

  class PySVObject;
  chandle pysv_ptr;
  endclass
  typedef class Foo;
  class Foo extends PySVObject;
    function new(input int num,
                input chandle ptr=null);
      if (ptr == null) begin
        pysv_ptr = Foo_pysv_init(num);
      end
      else begin
        pysv_ptr = ptr;
      end
    endfunction
    function int bar(input int num);
      return Foo_bar(pysv_ptr, num);
    endfunction
    function void destroy();
      Foo_destroy(pysv_ptr);
    endfunction
  endclass

Notice that every SystemVerilog wrapper class is inherited from the base class
``PySVObject``, which has an C pointer to the actual Python object. To allow
wrapper objects being created without the pointer only, we added additional
argument to the constructor, since SystemVerilog does not support function
overloading.

For the function ``foo_bar`` where the argument is of type ``Foo``, the
function is generated as follows, with proper function signature.

.. code-block:: SystemVerilog

  function int foo_bar(input Foo foo,
                      input int num);
    return foo_bar_(foo.pysv_ptr, num);
  endfunction

For cases where you need duck-type the Python objects, you can set the argument
or type to ``DataType.Object``. With that, ``PySVObject`` type will be used in
the signature, which avoids illegal downcast in SystemVerilog.

.. warning::

  The current implementation assumes certain ordering of class object creation.
  If you want to create a class inside a function and the class constructor
  hasn't been called in the SystemVerilog/C++ code yet, you will get a name
  error. This limitation only happens if the class is defined in the same file
  as the function. It should not be an issue if the class is imported from
  other modules, which could be a workaround.

  We will address this issue in the future releases.

To avoid memory leak from SystemVerilog's garbage collection, we provide a
"destructor" function called ``destory()``. You need to manually call this
method before the object goes out of scope, since SystemVerilog does not
support automatic destructor function.

The process to generate C++ binding is similar. You can use ``generate_cxx_binding``
as following:

.. code-block:: Python

  generate_cxx_binding([Foo, foo_bar], filename="pysv.hh")

The generated code follows the same structure as the SystemVerilog's. Here is the
class definition:

.. code-block:: C++

  class PySVObject {
  public:
    PySVObject() = default;
    PySVObject(void* ptr): pysv_ptr(ptr) {}
    PySVObject(const PySVObject &obj) : pysv_ptr(obj.pysv_ptr) {}
    virtual ~PySVObject() = default;

    void *pysv_ptr = nullptr;
  };
  class Foo : public PySVObject {
  public:
    Foo(int32_t num);
    int32_t bar(int32_t num);
    ~Foo() override;
    inline Foo(void *ptr): PySVObject(ptr) {}
  };

Unlike SystemVerilog, we have overloaded class constructor to accommodate different
usage scenarios.

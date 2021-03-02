.. _basics:

Basic usages
============
This section demonstrates the basic features of pysv.

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
To specify the argument type, we can add the types to the function decorator with given
argument name.

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

.. note::

  For more complex data type such as Python objects, please refer to :doc:`Object-Oriented Programming <advanced/oop>`.

If you wish to return multiple objects (i.e. tuple), due to the restriction of DPI typing system,
we need to specify the return tuple using `Reference` object. Here is a simple example:

.. code-block:: Python

    from pysv import sv, DataType, Reference

    @sv(return_type=Reference(a=DataType.UInt, b=DataType.Uint))
    def set_values():
        return 42, 43

In the example, we create a reference object to specify the return type names and their individual
types. pysv will unwrap the tuple and set the output accordingly. In SystemVerilog, we will see
the following function definition

.. code-block:: SystemVerilog

    function set_values(output int a, output int b);

Whereas in C/C++ we will see the following function definition:

.. code-block:: C++

    void set_values(int *a, int *b);

Notice that your function can take normal input arguments. All the output arguments will be
generated after the inputs.

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

There are more optional arguments provided with default values:

- ``lib_name``: library name. Default value is ``"pysv"``. You will see generated
  shared library in the form of ``lib${lib_name}.so``.
- ``release_build``: whether to use CMake release build. Default is ``False``. Using
  release build will significantly improve the C++-Python interface performance, at
  the cost of prolonged compilation time.
- ``clean_up_build``: whether to remove the build folder. Notice that pysv creates
  a ``build`` folder for CMake to compile. Set this option to ``True`` to remove that
  folder. This, however, does not remove the immediate code generated.
- ``add_sys_path``: whether to add system path. Default is ``False``. pysv uses a set
  of rules to detect whether user has imported a foreign module, and automatically
  set set system path if detected. However, should the rules fail, user can manually
  set this flag to ``True`` to force add system path.

Generate binding code
---------------------

pysv provides ability to generate both SystemVerilog and C++ bindings.
For object-oriented code generation,
please refer to :doc:`Object-Oriented Programming <advanced/oop>`.

.. _sv-binding:

SystemVerilog binding
~~~~~~~~~~~~~~~~~~~~~
``generate_sv_binding`` is the function you need to generate the SystemVerilog
binding. Below is an example usage:

.. code-block:: Python

  binding = generate_sv_binding([hello_world])

The first argument takes in a list of function names that's been decorated with
``@sv``. An exception will thrown if pysv detects that the function has not been
done so.

There are some optional arguments provided with default values:

- ``pkg_name``: the SystemVerilog package name. If not set, ``pysv`` is used.
- ``pretty_print``: whether to format the code based on some coding style. Default
  is ``True``.
- ``filename``: if provided, pysv will write the binding code to the specified
  filename.

.. note::

  ``generate_sv_binding`` always returns the string content of the binding,
  regardless whether the binding has been written to a file or not.

Below is the generated SystemVerilog function signature with our hello world example:

.. code-block:: SystemVerilog

  function void hello_world();

.. _cxx-binding:

C++ binding
~~~~~~~~~~~
``generate_cxx_binding`` is the function you need to generate the C++ binding. Below
is an example uage:

.. code-block:: Python

  binding = generate_cxx_binding([hello_world])

The first argument takes in a list of function names that's been decorated with
``@sv``. An exception will thrown if pysv detects that the function has not been
done so.

There are some optional arguments provided with default values:

- ``namespace``: the C++ namespace name. If not set, ``pysv`` is used.
- ``pretty_print``: whether to format the code based on some coding style. Default
  is ``True``.
- ``filename``: if provided, pysv will write the binding code to the specified
  filename.
- ``include_implementation``: if set to ``True``, the actual C++ implemented will be
  generated as well. Only for debugging, since the functions are not declared as
  ``inline`` and will likely trigger a linker error.

.. note::

  ``generate_cxx_binding`` always returns the string content of the binding,
  regardless whether the binding has been written to a file or not.

Below is the generated C++ function signature with our hello world example:

.. code-block:: C++

  void hello_world();


Import foreign modules
----------------------
pysv can automatically detect any foreign module being used in the current working scope and
modify the system path which python interpreter uses to search modules accordingly. 

Currently supported import semantics:

- Python modules, e.g.:
   .. code-block:: Python

     import numpy
     import tensorflow as tf

- Python classes from a module, e.g.:

   .. code-block:: Python

     from tensorflow import Tensor

- Python functions from a module, e.g.:

   .. code-block:: Python

     from numpy import min

Due to the current implementation limitation, however, functions or classes created from
local scope are not supported and exception will be thrown when pysv detects that.
One workaround is to create or import such functions/class inside the decorated function.


Shutdown the Python runtime
---------------------------

pysv maintains several global state to ensure the liveness of Python objects. These global
data structures need to be destroyed before simulation finishes, otherwise you may get
a segfault depends on how simulator frees up memory. pysv generates ``pysv_finalize()``
function in SystemVerilog and C++ binding code so users can call it at the end of
simulation.

.. warning::

  For a small-scale simulation, especially with Verilator or no foreign modules are imported,
  ending simulation without calling ``pysv_finalize()`` will be fine in most cases. However,
  it is the best practice to call it at the end of simulation.

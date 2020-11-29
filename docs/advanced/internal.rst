.. _internal:

How pysv works
==============

pysv relies heavily on pybind11 to interface with Python interpreter.


Function code generation
------------------------
Every Python function is directly embedded into corresponding C function
as shown below:

.. code-block:: C++
  
    extern "C" {
    __attribute__((visibility("default"))) int32_t foo() {
        auto globals = py::dict();
        auto locals = py::dict();

        py::exec(R"(
        def foo():
            return 42

        __result = foo()
        )", globals, locals);
        return locals["__result"].cast<int32_t>();
    }
    }

The entire function is declared inside extern C block and marked with proper
visibility to ensure that normal C code can link against it, which is a
requirement for SystemVerilog DPI calls.

There will be an overhead of redundant parsing of the same functions if
it is called multiple times. We will improve it in the future release.

Imports
-------
pysv looks through the call stack ``globals()`` and stores the import
information for each ``@sv()``. Then it dumps the imported objects' name
into the generated C++ code, which will be load up then first time the
object is imported:

.. code-block:: Python

  import numpy as np

  @sv()
  def foo():
    pass


.. code-block:: C++

    auto globals = py::dict();
    import_module("numpy", "np", globals);
  

Foreign definitions
-------------------
pysv inspects the imports and see if there is any
foreign modules have been imported and not in the system module. If any
foreign object is detected, pysv will dump the current ``sys.path`` into
the generated C++ code and have the Python interpreter load it when initialize
the pysv runtime, as shown below:

.. code-block:: C++

  auto SYS_PATH = {"/tmp/example",
                   "/usr/lib/python38.zip",
                   "/usr/lib/python3.8",
                   "/usr/lib/python3.8/lib-dynload",
                   "/tmp//env/lib/python3.8/site-packages"};

  // add to sys.path later during initialization
  for (auto const &path: SYS_PATH) {
      sys.attr("path").attr("append")(py::str(path));
  }

.. note::

  The dumped ``sys.path`` content is in absolute path, which implies that the
  simulator needs to have access to these directories for the interpreter to
  load foreign modules. It is recommended to compile pysv and simulate the test
  bench using the same filesystem.


SystemVerilog bindings
----------------------

The SystemVerilog standard provides a connivent way, called DPI_, to import C
functions into SystemVerilog. pysv uses DPI to import generated functions
into SystemVerilog and then wrap them using SystemVerilog semantics if needed.

Here is an example to see generated SystemVerilog class definition

.. code-block:: Python 

    class Foo:
    def __init__(self):
        pass

    @sv()
    def bar(self):
        return 42


.. code-block:: SystemVerilog

    package pysv;
    import "DPI-C" function chandle Foo_pysv_init();
    import "DPI-C" function int Foo_bar(input chandle self);
    import "DPI-C" function void Foo_destroy(input chandle self);
    import "DPI-C" function void pysv_finalize();
    class PySVObject;
    chandle pysv_ptr;
    endclass
    class Foo extends PySVObject;
    function new();
        pysv_ptr = Foo_pysv_init();
    endfunction
    function int bar();
        return Foo_bar(pysv_ptr);
    endfunction
    function void destroy();
        Foo_destroy(pysv_ptr);
    endfunction
    endclass
    endpackage


Notice that the class methods is flattened into normal function where the first
argument is the C pointer. Each generated class will hold a pointer to its
corresponding Python class object.


.. _DPI: https://en.wikipedia.org/wiki/SystemVerilog_DPI

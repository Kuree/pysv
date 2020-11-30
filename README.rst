pysv: Running Python Code in SystemVerilog
===================================================

|Latest Documentation Status| |Github CI| |Buildkite CI| |PyPI package|

**pysv** is a lightweight Python library that allows functional models
to be written in Python and then executed inside standard SystemVerilog
simulators, via DPI.

Core Features
-------------

pysv is designed to be versatile and can be used directly or as a
library in other hardware generator frameworks. It offers the following
features:

-  C/C++ and SystemVerilog binding code generation
-  Foreign modules, e.g. ``numpy`` or ``tensorflow``.
-  Python functions
-  Python classes
-  Platform-independent compilation

Supported Simulators
--------------------

Theoretically any simulator that supports SystemVerilog DPI semantics
should work. Here is a list of simulators that have been tested:

-  Cadence® Xcelium™
-  Synopsys VCS®
-  Mentor Questa®
-  Vivado® Simulator
-  Verilator

Dependencies
------------

pysv leverages `pybind11`_ to execute arbitrary Python code. As a
result, here is a list of dependencies

-  cmake 3.4 or newer
-  Any C++ compiler that supports C++11:

   -  Clang/LLVM 3.3 or newer (for Apple Xcode’s clang, this is 5.0.0 or
      newer)
   -  GCC 4.8 or newer

-  Python 3.6 or newer

Usage Example
-------------

Here is a simple example to show a Python class that uses ``numpy`` for
computation.

.. code:: python

   import numpy as np
   from pysv import sv, compile_lib, DataType, generate_sv_binding

   class Array:
       def __init__(self):
           # constructor without any extra argument is exported to SV directly
           self.__array = []

       @sv()
       def add_element(self, i):
           self.__array.append(i)

       @sv()
       def min(self):
           # call the numpy function
           return np.min(self.__array)

       @sv(return_type=DataType.Bit)
       def exists(self, value):
           return self.__exists(value)

       def __exists(self, value):
           # this function is not exposed to SystemVerilog
           return value in self.__value

   # compile the code into a shared library for DPI to load
   # build the lib inside the ./build folder
   # lib_path is the path to the shared library file
   lib_path = compile_lib([Array], cwd="build")
   # generate SV bindings
   generate_sv_binding([Array], filename="array_pkg.sv", pkg_name="demo")

Now we can use the class directly with the SystemVerilog binding:

.. code:: SystemVerilog

    // import Array
    import demo::*;

    Array a = new();
    a.add_element(1);
    assert(a.exists(1));
    assert(!a.exists(2));
    // numpy under the hood!
    assert(a.min() == 1);


.. _pybind11: https://github.com/pybind/pybind11
.. |Latest Documentation Status| image:: https://readthedocs.org/projects/pysv/badge/?version=latest
  :target: https://pysv.readthedocs.io/?badge=latest
.. |Github CI| image:: https://github.com/Kuree/pysv/workflows/CI%20Test/badge.svg
  :target: https://github.com/Kuree/pysv/actions?query=branch%3Amaster
.. |Buildkite CI| image:: https://badge.buildkite.com/84280442c566d340f8cafdce06463b5c47d59c88162a4948ba.svg
  :target: https://buildkite.com/stanford-aha/pysv
.. |PyPI package| image:: https://img.shields.io/pypi/v/pysv?color=blue
  :target: https://pypi.org/project/pysv/
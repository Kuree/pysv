pysv: Running Python Code in SystemVerilog
===================================================

**pysv** is a lightweight Python library that allows functional models
to be written in Python and then executed inside standard SystemVerilog
simulators, via DPI.

Core Features
-------------

pysv is designed to be versatile and can be used directly or as a
library in other hardware generator frameworks. It offers the following
features:

-  C and SystemVerilog header code generation
-  Foreign modules, e.g. ``numpy`` or ``tensorflow``.
-  Python functions
-  Python classes
-  Platform-independent compilation

Supported Simulators
--------------------

Theoretically any simulator that supports SystemVerilog DPI semantics
should work. Here is a list of simulators that have been tested:

-  Xcelium/Incisive
-  vcs
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
   from pysv import sv, compile_lib, DataType

   class Array:
       @sv()
       def __init__(self):
           super().__init__()
           self.__array = []

       @sv()
       def add_element(self, i):
           self.__array.append(i)

       @sv()
       def min(self):
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

.. _pybind11: https://github.com/pybind/pybind11

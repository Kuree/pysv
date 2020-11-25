.. _install:

Installing the library
======================

pysv is a pure Python library and can be installed via the following command:

.. code-block::

    pip install pysv


Environment setup
-----------------

Although pysv is a Python package, in order to run Python code in
SystemVerilog, we need a complete C++ tool-chain.  Below are system environment
requirements:

- cmake 3.4 or newer
- Any C++ compiler that supports C++11:

  - Clang/LLVM 3.3 or newer (for Apple Xcode’s clang, this is 5.0.0 or newer)
  - GCC 4.8 or newer
- Python 3.6 or newer

That being said, it should run smoothly in most systems since all it needs is
a C++11 capable compiler. If your system's default cmake is too old, you can
try to use the one from PyPI:

.. code-block::

    pip install cmake


SystemVerilog simulators
------------------------

pysv is designed to be simulator agonistic: it can work with virtually any
simulator that supports DPI function calls. Since pysv generates C++ code,
it naturally supports Verilator. Here is a list of simulators that pysv has
been tested one

- Cadence® Xcelium™
- Synopsys VCS®
- Mentor Questa®
- Vivado® Simulator
- Verilator

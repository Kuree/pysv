.. _verilator:

Use pysv with Verilator
=======================

This sections will cover usages with Verilator.
Too see how to generate C++ binding with classes, please refer to
:ref:`cxx-binding` and :doc:`oop`.

1. In the verilator command, include the shared library and the generated
   binding file, e.g.

  .. code-block::
    
    verilator --cc design1.sv design2.sv top.cc pysv_cxx.hh libpysv.so

2. Make sure ``libpysv.so`` is in your ``LD_LIBRARY_PATH`` when you run
   the test bench binary, e.g.

  .. code-block::

    LD_LIBRARY_PATH=. ./obj_dir/Vtop

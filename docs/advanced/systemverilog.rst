.. _systemverilog:

Use pysv with SystemVerilog
===========================

This section covers usages with common SystemVerilog simulators.
To see how to generate SystemVerilog binding with classes,
please refer to :ref:`sv-binding` and :doc:`oop`.

Cadence® Xcelium™
-----------------

In your file list, make sure that the binding package is loaded before the
files that use it. You need `-sv_lib` switch to tell the simulator to load
the compiled binary. Here is an example of ``xrun`` command if you use
the default names:

.. code-block::

  xrun design1.sv design2.sv pysv_pkg.sv top.sv -sv_lib build/libpysv.so

Synopsys VCS®
-------------

VCS follows the exact same flag as Xcelium:

.. code-block::

  vcs design1.sv design2.sv pysv_pkg.sv top.sv -sverilog -sv_lib build/libpysv.so

Notice that we need the additional `-sverilog` flag to let the parser switch to
SystemVerilog mode.

Mentor Questa®
--------------

In the ``vsim`` command, add ``-sv_lib`` as well. Notice that we don't need the
``.so`` extension when providing the path to the shared library.


Vivado® Simulator
-----------------

Depends on how you create your test bench, there are many different ways to
set up. We will cover the command line options here.

In the ``xelab`` command, use ``--sv_lib`` switch and provide the library path
without the ``.so`` extension.

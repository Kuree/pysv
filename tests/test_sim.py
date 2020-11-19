import pysv.util
from pysv import sv, compile_lib, DataType, generate_cxx_binding, generate_sv_binding
from importlib.util import find_spec
import tempfile
import pytest
import os
import numpy as np


class BoxFilter:
    @sv()
    def __init__(self, filter_size):
        self.__values = [0 for _ in range(filter_size)]
        self.__ptr = 0

    @sv(value=DataType.UInt)
    def push(self, value):
        self.__values[self.__ptr] = value
        self.__ptr = (self.__ptr + 1) % len(self.__values)

    @sv(return_type=DataType.UInt)
    def avg(self):
        # use numpy to implement average
        return int(np.average(self.__values))


@pytest.mark.skipif(not pysv.util.is_verilator_available(), reason="Verilator not available")
def test_verilator(get_vector_filename):
    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([BoxFilter], cwd=temp)
        header_file = os.path.join(os.path.abspath(temp), "box_filter.hh")
        generate_cxx_binding([BoxFilter], filename=header_file)

        # we have three files
        # the sv file, the driver file, and the header
        sv_file = get_vector_filename("box_filter.sv")
        driver = get_vector_filename("test_verilator_boxfilter.cc")
        # just run teh verilator
        tester = pysv.util.VerilatorTester(lib_path, sv_file, header_file, driver, cwd=temp)
        tester.run()


simulator_map = {
    "vcs": (pysv.util.is_vcs_available, pysv.util.VCSTester),
    "xcelium": (pysv.util.is_xcelium_available, pysv.util.XceliumTester),
    "questa": (pysv.util.is_questa_available, pysv.util.QuestaTester),
    "vivado": (pysv.util.is_vivado_available, pysv.util.VivadoTester)
}


@pytest.mark.parametrize("simulator", ("xcelium", "vcs", "questa", "vivado"))
def test_sv_simulator(get_vector_filename, simulator):
    avail, tester_cls = simulator_map[simulator]
    if not avail():
        pytest.skip("{0} not available".format(simulator))
    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([BoxFilter], cwd=temp)
        sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
        generate_sv_binding([BoxFilter], filename=sv_pkg)
        sv_file = get_vector_filename("box_filter.sv")
        tb_file = get_vector_filename("test_sv_boxfilter.sv")

        tester = tester_cls(lib_path, sv_pkg, sv_file, tb_file, cwd=temp)
        tester.run()


@pytest.mark.skipif(find_spec("tensorflow") is None, reason="Tensorflow not installed")
def test_tensorflow(get_vector_filename):
    # should work with any simulator, but it seems like the Xcelium we have doesn't ship
    # with the latest libstdc++. Use vcs instead
    avail, tester_cls = simulator_map["vcs"]
    if not avail():
        pytest.skip("VCS not available")
    import tensorflow as tf

    @sv()
    def simple_mat_mal(a, b):
        c = tf.constant([[a, a], [a, a]])
        d = tf.constant([[b, b], [b, b]])
        e = tf.matmul(c, d)
        n = e.numpy()
        s = np.sum(n)
        return s

    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([simple_mat_mal], cwd=temp)
        sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
        generate_sv_binding([simple_mat_mal], filename=sv_pkg)
        tb_file = get_vector_filename("test_tensorflow.sv")

        tester = tester_cls(lib_path, sv_pkg, tb_file, cwd=temp)
        tester.run()


if __name__ == "__main__":
    from conftest import get_vector_filename_fn
    test_tensorflow(get_vector_filename_fn)



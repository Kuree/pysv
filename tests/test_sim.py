import pysv.util
from pysv import sv, compile_lib, DataType, generate_cxx_binding, generate_sv_binding, Reference
from importlib.util import find_spec
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
def test_verilator(get_vector_filename, temp):
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
def test_sv_simulator(get_vector_filename, simulator, temp):
    avail, tester_cls = simulator_map[simulator]
    if not avail():
        pytest.skip("{0} not available".format(simulator))

    lib_path = compile_lib([BoxFilter], cwd=temp)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([BoxFilter], filename=sv_pkg)
    sv_file = get_vector_filename("box_filter.sv")
    tb_file = get_vector_filename("test_sv_boxfilter.sv")

    tester = tester_cls(lib_path, sv_pkg, sv_file, tb_file, cwd=temp)
    tester.run()


@pytest.mark.skipif(find_spec("tensorflow") is None, reason="Tensorflow not installed")
def test_tensorflow(get_vector_filename, temp):
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

    lib_path = compile_lib([simple_mat_mal], cwd=temp)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([simple_mat_mal], filename=sv_pkg)
    tb_file = get_vector_filename("test_tensorflow.sv")

    tester = tester_cls(lib_path, sv_pkg, tb_file, cwd=temp)
    tester.run()


@pytest.mark.parametrize("simulator", ("xcelium", "vcs"))
def test_sv_object_funcs(get_vector_filename, simulator, temp):
    avail, tester_cls = simulator_map[simulator]
    if not avail():
        pytest.skip(simulator + " is not available")

    class ClassA:
        @sv()
        def __init__(self):
            self.num = 21

    class ClassB:
        # object is allowed if you want duct typing
        @sv(a=DataType.Object)
        def __init__(self, a):
            self.a = a

        @sv(return_type=ClassA)
        def create_a(self, num):
            a = ClassA()
            a.num = num
            return a

        @sv(a=ClassA)
        def add(self, a):
            return self.a.num + a.num

    lib_path = compile_lib([ClassA, ClassB], cwd=temp)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([ClassA, ClassB], filename=sv_pkg)
    tb_file = get_vector_filename("test_sv_object_funcs.sv")

    tester = tester_cls(lib_path, sv_pkg, tb_file, cwd=temp)
    tester.run()


def test_sv_object_funcs_2(get_vector_filename, temp):
    # test out a normal function takes in Python object
    simulator = "xcelium"
    avail, tester_cls = simulator_map[simulator]
    if not avail():
        pytest.skip(simulator + " is not available")

    class ClassA2:
        @sv()
        def __init__(self):
            self.num = 1

    @sv(a=ClassA2)
    def add(a):
        return a.num + 41

    lib_path = compile_lib([ClassA2, add], cwd=temp)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([ClassA2, add], filename=sv_pkg)
    tb_file = get_vector_filename("test_sv_object_funcs_2.sv")

    tester = tester_cls(lib_path, sv_pkg, tb_file, cwd=temp)
    tester.run()


def test_sv_return_reference(get_vector_filename, temp):
    # test out return reference
    simulator = "xcelium"
    avail, tester_cls = simulator_map[simulator]
    if not avail():
        pytest.skip(simulator + " is not available")

    @sv(return_type=Reference(a=DataType.Int, b=DataType.Int))
    def set_value():
        return 42, 43

    lib_path = compile_lib([set_value], cwd=temp)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([set_value], filename=sv_pkg)
    tb_file = get_vector_filename("test_sv_return_reference.sv")

    tester = tester_cls(lib_path, sv_pkg, tb_file, cwd=temp)
    tester.run()


@pytest.mark.skipif(not pysv.util.is_verilator_available(), reason="Verilator not available")
def test_verilator_return_reference(get_vector_filename, temp):
    @sv(return_type=Reference(a=DataType.UInt, b=DataType.UInt))
    def set_value():
        return 42, 43

    lib_path = compile_lib([set_value], cwd=temp)
    header_file = os.path.join(os.path.abspath(temp), "test_verilator_return_ref.hh")
    generate_cxx_binding([set_value], filename=header_file)

    # we have three files
    # the sv file, the driver file, and the header
    sv_file = get_vector_filename("test_verilator_return_ref.sv")
    driver = get_vector_filename("test_verilator_return_ref.cc")
    # just run teh verilator
    tester = pysv.util.VerilatorTester(lib_path, sv_file, header_file, driver, cwd=temp)
    tester.run()


@pytest.mark.skipif(not pysv.util.is_verilator_available(), reason="Verilator not available")
def test_verilator_array(get_vector_filename, temp):
    @sv(a=DataType.IntArray[2])
    def set_value(a):
        print(a[2, 1])
        a[2, 1] = 42

    lib_path = compile_lib([set_value], cwd=temp)
    header_file = os.path.join(os.path.abspath(temp), "test_verilator_array.hh")
    generate_cxx_binding([set_value], filename=header_file)
    sv_pkg = os.path.join(os.path.abspath(temp), "pysv_pkg.sv")
    generate_sv_binding([set_value], filename=sv_pkg)

    # we have three files
    # the sv file, the driver file, and the header
    sv_file = get_vector_filename("test_verilator_array.sv")
    driver = get_vector_filename("test_verilator_array.cc")
    # just run the verilator
    tester = pysv.util.VerilatorTester(lib_path, sv_file, header_file, driver, cwd=temp)
    out = tester.run().decode("ascii")
    assert out == "2\n42\n"


if __name__ == "__main__":
    from conftest import get_vector_filename_fn
    test_verilator_array(get_vector_filename_fn, "temp")


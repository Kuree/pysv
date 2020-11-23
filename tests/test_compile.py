from pysv import compile_lib, sv, DataType
import os
import tempfile
from pysv.compile import compile_and_run


def test_compile():
    @sv()
    def add(a, b):
        return a + b
    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([add], cwd=temp)
        assert os.path.exists(lib_file)


def test_str():
    @sv(s=DataType.String, return_type=DataType.String)
    def mul_str(num, s):
        return num * s

    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([mul_str], cwd=temp)
        code = """
        const char *str = "test ";
        int32_t repeat = 4;
        auto r1 = mul_str(repeat, str);
        std::cout << r1 << std::endl;
        // another call
        auto r2 = mul_str(repeat + 1, str);
        std::cout << r2;
        """

        outputs = compile_and_run(lib_file, code, temp, [mul_str])
        outputs = outputs.splitlines()
        assert outputs[0] == "test " * 4
        assert outputs[1] == "test " * (4 + 1)


def test_numpy():
    import numpy as np

    @sv()
    def min_(a, b):
        return np.min([a, b])

    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([min_], cwd=temp)
        call_str = min_.make_call(-1, -2).str()
        code = """
        auto r = {0};
        std::cout << r << std::endl;
        """.format(call_str)

        outputs = compile_and_run(lib_file, code, temp, [min_])
        assert int(outputs) == -2


def test_empty_global():
    @sv()
    def foo():
        pass

    foo.func_def.imports = {}
    with tempfile.TemporaryDirectory() as temp:
        compile_lib([foo], cwd=temp)


def test_type_import():
    from random import Random

    @sv()
    def foo():
        rand = Random()
        rand.seed(0)
        val = rand.randint(0, 42)
        print(val)

    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([foo], cwd=temp)
        call_str = foo.make_call().str() + ";\n"
        value = compile_and_run(lib_file, call_str, temp, [foo])
        value = int(value)
        rand = Random()
        rand.seed(0)
        expected = rand.randint(0, 42)
        assert value == expected


def test_no_call_sv_compile():
    from pysv.codegen import generate_cxx_binding, generate_sv_binding

    @sv
    def foo():
        pass

    with tempfile.TemporaryDirectory() as temp:
        compile_lib([foo], cwd=temp)
        generate_cxx_binding([foo], filename=os.path.join(temp, "test.hh"))
        generate_sv_binding([foo], filename=os.path.join(temp, "test.svh"))


def test_function_import():
    from random import randint

    @sv()
    def rand_():
        print(randint(0, 42))

    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([rand_], cwd=temp)
        call_str = rand_.make_call().str() + ";\n"
        value = compile_and_run(lib_file, call_str, temp, [rand_])
        value = int(value)
        # randint is [a, b]
        assert value in range(0, 42 + 1)


if __name__ == "__main__":
    test_function_import()

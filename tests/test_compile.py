from pysv import compile_lib, dpi, DataType, set_run_function
import os
import tempfile
from pysv.util import compile_and_run, simply_dpi_call_compile


def test_compile():
    @dpi()
    def add(a, b):
        return a + b
    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([add], cwd=temp)
        assert os.path.exists(lib_file)


def test_str():
    @dpi(s=DataType.String, return_type=DataType.String)
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

    @dpi()
    def min_(a, b):
        return np.min([a, b])

    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([min_], cwd=temp)
        call_str = simply_dpi_call_compile(min_, -1, -2)
        code = """
        auto r = {0};
        std::cout << r << std::endl;
        """.format(call_str)

        outputs = compile_and_run(lib_file, code, temp, [min_])
        assert int(outputs) == -2


if __name__ == "__main__":
    test_numpy()

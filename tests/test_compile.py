from pysv import compile_lib, dpi
import os
import tempfile


def test_compile():
    @dpi()
    def add(a, b):
        return a + b
    with tempfile.TemporaryDirectory() as temp:
        lib_file = compile_lib([add], cwd=temp)
        assert os.path.exists(lib_file)


if __name__ == "__main__":
    test_compile()

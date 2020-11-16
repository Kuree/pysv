import sys  # don't remove this import
from pysv import sv, compile_lib
from pysv.compile import compile_and_run
from pysv.function import DPIFunctionCall
from pysv.model import get_dpi_functions
from pysv.pyast import get_class_src
import tempfile


class TestModel:
    __test__ = False

    @sv()
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    @sv()
    def foo(self, value):
        return value + self.value1 - self.value2


def test_class_function():
    # making sure we can work with the class as if the DPI doesn't
    # exist
    m = TestModel(42, 2)
    v = m.foo(2)
    assert v == 42


def test_class_init():
    model_func = TestModel.__init__
    assert isinstance(model_func, DPIFunctionCall)
    model_func = model_func.func_def
    assert len(model_func.imports) >= 1
    assert model_func.imports["sys"] == "sys"
    assert model_func.func_name == "TestModel___init__"


def test_get_dpi_func():
    dpi_funcs = get_dpi_functions(TestModel)
    assert len(dpi_funcs) > 1
    found = False
    for func in dpi_funcs:
        if func.func_name == "TestModel_foo":
            found = True
    assert found


def test_model_src():
    src = get_class_src(TestModel)
    assert "@dpi()" not in src


def test_model_constructor():
    c_code = """
    void *ptr = {0}(42, 1);
    std::cout << ptr;
    """.format(TestModel.__init__.func_name)
    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([TestModel], cwd=temp)
        compile_and_run(lib_path, c_code, temp, [TestModel])


def test_model_function_call():
    c_code = """
    void *ptr = {0}(42, 1);
    auto r = {1}(ptr, 1);
    std::cout << r;
    """.format(TestModel.__init__.func_name, TestModel.foo.func_name)
    with tempfile.TemporaryDirectory() as temp:
        calls = [TestModel]
        lib_path = compile_lib(calls, cwd=temp)
        output = compile_and_run(lib_path, c_code, temp, calls)
        assert int(output) == 42


if __name__ == "__main__":
    test_model_function_call()

import sys  # don't remove this import
from pysv import PySVModel, dpi, compile_lib
from pysv.util import compile_and_run
import tempfile


class TestModel(PySVModel):
    __test__ = False

    def __init__(self, value1, value2):
        super().__init__()
        self.value1 = value1
        self.value2 = value2

    @dpi()
    def foo(self, value):
        return value + self.value1 - self.value2


def test_class_init():
    model = TestModel(42, 1)
    assert len(model.imports) >= 1
    assert model.imports["sys"] == "sys"
    assert model.func_name == "TestModel__init__"
    # notice that the first args is self
    assert model.args[0 + 1] == 42
    assert model.args[1 + 1] == 1


def test_get_parent_class():
    model = TestModel(42, 1)
    foo = model.foo
    assert foo.func_def.parent_class == model
    # call again
    foo = model.foo
    assert foo.func_def.parent_class == model
    assert foo.func_def.func_name == "TestModel_foo"


def test_model_src():
    model = TestModel(42, 1)
    src = model.get_func_src()
    assert "@dpi()" not in src


def test_model_constructor():
    model = TestModel(42, 1)
    c_code = """
    void *ptr = {0}(42, 1);
    std::cout << ptr;
    """.format(model.func_name)
    with tempfile.TemporaryDirectory() as temp:
        lib_path = compile_lib([model], cwd=temp)
        compile_and_run(lib_path, c_code, temp, [model])


def test_model_function_call():
    model = TestModel(42, 1)
    c_code = """
    void *ptr = {0}(42, 1);
    auto r = {1}(ptr, 1);
    std::cout << r;
    """.format(model.func_name, model.foo.func_name)
    with tempfile.TemporaryDirectory() as temp:
        calls = [model, model.foo]
        lib_path = compile_lib(calls, cwd=temp)
        output = compile_and_run(lib_path, c_code, temp, calls)
        assert int(output) == 42


if __name__ == "__main__":
    test_model_function_call()

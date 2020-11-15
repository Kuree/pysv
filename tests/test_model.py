import sys  # don't remove this import
from pysv import PySVModel, dpi


class TestModel(PySVModel):
    __test__ = False

    def __init__(self, value1, value2):
        super().__init__()
        self.value1 = value1
        self.value2 = value2

    @dpi()
    def foo(self):
        return 1


def test_class_init():
    model = TestModel(42, 1)
    assert len(model.imports) == 1
    assert model.imports["sys"] == "sys"
    assert model.func_name == "TestModel__init__"


def test_get_parent_class():
    model = TestModel(42, 1)
    foo = model.foo
    assert foo.func_def.parent_class == TestModel
    # call again
    foo = model.foo
    assert foo.func_def.parent_class == TestModel
    assert foo.func_def.func_name == "TestModel_foo"


def test_model_src():
    model = TestModel(42, 1)
    src = model.get_func_src()
    assert "@dpi()" not in src


if __name__ == "__main__":
    test_model_src()

import sys
from pysv import PySVModel, dpi


class TestModel(PySVModel):
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
    model.func_name = "TestModel__init__"


def test_get_parent_class():
    model = TestModel(42, 1)
    foo = model.foo
    assert foo.func_def.parent_class == TestModel
    # call again
    foo = model.foo
    assert foo.func_def.parent_class == TestModel
    assert foo.func_def.func_name == "TestModel_foo"


if __name__ == "__main__":
    test_get_parent_class()

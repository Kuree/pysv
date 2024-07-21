from pysv import sv, DataType, is_run_function_set, set_run_function, import_


def test_frame_import():
    import os as os_

    @sv()
    def func():
        pass

    assert "os_" in func.func_def.imports
    assert "os" == func.func_def.imports["os_"]
    assert func.func_def.func.__name__ == "func"


def test_width():
    @sv()
    def func1():
        return 1

    @sv(DataType.Bit)
    def func2():
        pass

    # by default the width is Int
    assert func1.func_def.return_type == DataType.Int
    assert func2.func_def.return_type == DataType.Bit


def test_arg():
    @sv(a=DataType.ShortInt)
    def func1(a, b):
        pass

    assert func1.func_def.arg_types["a"] == DataType.ShortInt
    # default type
    assert func1.func_def.arg_types["b"] == DataType.Int
    # ordering
    assert len(func1.func_def.arg_names) == 2
    assert func1.func_def.arg_names[0] == "a"
    assert func1.func_def.arg_names[1] == "b"


def test_func_name():
    @sv()
    def func_name():
        pass

    assert func_name.func_def.func_name == "func_name"


def test_get_src():
    @sv()
    def func(a, b):
        return a + b
    src = func.func_def.get_func_src()
    assert src == \
        """def func(a, b):
    return a + b
"""


def test_run_function():
    assert is_run_function_set()

    @sv()
    def add(a, b):
        return a + b

    assert add(41, 1) == 42
    set_run_function(False)
    r = add(41, 1)
    assert not isinstance(r, int)
    set_run_function(True)


def test_auto_set_return():
    @sv()
    def foo():
        a = 1

    func_call = foo
    assert func_call.func_def.return_type == DataType.Void


def test_local_type_import():
    class A:
        def foo(self):
            print("foo")

    @sv()
    def foo():
        a = A()
        a.foo()

    assert "A" not in foo.func_def.imports


def test_explicit_import():
    import random

    @sv(imports={"RND": random.Random})
    def foo():
        pass

    assert "RND" in foo.func_def.imports
    assert foo.func_def.imports["RND"] == "random.Random"
    assert len(foo.func_def.imports) == 1


def test_no_call_sv():
    @sv
    def foo():
        pass

    assert isinstance(foo, sv)


def test_import():
    @import_
    def foo(a):
        pass

    assert isinstance(foo, import_)


if __name__ == "__main__":
    test_import()

from pysv import sv
from pysv.util import should_add_sys_path, make_unique_func_defs, clear_imports


def test_should_add_sys_path():
    @sv()
    def foo():
        pass

    foo.func_def.imports = {"tempfile": "tempfile", "os": "os", "pysv": "pysv"}
    assert not should_add_sys_path([foo])
    foo.func_def.imports = {"numpy": "numpy"}
    assert should_add_sys_path([foo])


def test_make_unique_func_defs():
    class Foo:
        @sv()
        def bar(self):
            pass

    assert len(make_unique_func_defs([Foo, Foo.bar])) == 1
    assert len(make_unique_func_defs([Foo.bar])) == 1
    assert make_unique_func_defs([Foo.bar])[0] == Foo
    assert len(make_unique_func_defs([Foo.bar, Foo, Foo.bar])) == 1


def test_clear_imports():
    import os

    @sv()
    def foo():
        pass

    before = foo.func_def.imports
    assert "os" in before
    clear_imports(foo)
    assert len(before) == 0


if __name__ == "__main__":
    test_clear_imports()

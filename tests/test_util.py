from pysv import sv
from pysv.util import should_add_sys_path, make_unique_func_defs


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


if __name__ == "__main__":
    test_make_unique_func_defs()

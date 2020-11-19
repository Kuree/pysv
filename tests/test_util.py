from pysv import sv
from pysv.util import should_add_sys_path


def test_should_add_sys_path():
    @sv()
    def foo():
        pass

    foo.func_def.imports = {"tempfile": "tempfile", "os": "os", "pysv": "pysv"}
    assert not should_add_sys_path([foo])
    foo.func_def.imports = {"numpy": "numpy"}
    assert should_add_sys_path([foo])


if __name__ == "__main__":
    test_should_add_sys_path()

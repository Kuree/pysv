from pysv import get_dpi_definition, dpi, DataType
from pysv.codegen import get_python_src, generate_c_function
# all the module imports in this file should be local to avoid breaking assertions


def test_get_dpi_definition():
    @dpi(a=DataType.String, b=DataType.Byte, return_type=DataType.CHandle)
    def func(a, b):
        return a + b

    result = get_dpi_definition(func)
    expected = 'import "DPI-C" function chandle func(input string a,\n' \
               '                                     input byte b);'
    assert result == expected

    result = get_dpi_definition(func, pretty_print=False)
    expected = 'import "DPI-C" function chandle func(input string a, input byte b);' # noqa
    assert expected == result


def test_get_python_src():
    import os as o
    import sys

    @dpi()
    def func(a, b):
        return a + b

    result = get_python_src(func)
    expected = """import os as o
import sys
def func(a, b):
    return a + b

__result = func(__a, __b)
"""
    assert result == expected


@dpi()
def simple_func(a, b, c):
    return a + b - c


def test_generate_c_function(check_file):
    result = generate_c_function(simple_func)
    check_file(result, "test_generate_c_function.cc")


if __name__ == "__main__":
    from conftest import check_file_fn
    test_generate_c_function(check_file_fn)

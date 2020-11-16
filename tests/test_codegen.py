from pysv import generate_dpi_definition, dpi, DataType
from pysv.codegen import (get_python_src, generate_cxx_function, generate_c_header, generate_cxx_code,
                          generate_dpi_definition)
# all the module imports in this file should be local to avoid breaking assertions


def test_get_dpi_definition():
    @dpi(a=DataType.String, b=DataType.Byte, return_type=DataType.CHandle)
    def func(a, b):
        return a + b

    result = generate_dpi_definition(func)
    expected = 'import "DPI-C" function chandle func(input string a,\n' \
               '                                     input byte b);'
    assert result == expected

    result = generate_dpi_definition(func, pretty_print=False)
    expected = 'import "DPI-C" function chandle func(input string a, input byte b);' # noqa
    assert expected == result


def test_get_python_src():
    import os as o
    import sys

    @dpi()
    def func(a, b):
        return a + b

    result = get_python_src(func)
    expected = """def func(a, b):
    return a + b

__result = func(__a, __b)
"""
    assert result == expected


@dpi()
def simple_func(a, b, c):
    return a + b - c


def test_generate_cxx_function(check_file):
    result = generate_cxx_function(simple_func, add_sys_path=False)
    check_file(result, "test_generate_cxx_function.cc")


def test_generate_c_header():
    result = generate_c_header(simple_func, pretty_print=False)
    assert result == "int32_t simple_func(int32_t a, int32_t b, int32_t c);"


def test_generate_cxx_code(check_file):
    result = generate_cxx_code([simple_func], add_sys_path=False)
    check_file(result, "test_generate_cxx_code.cc")


def test_generate_dpi_header(check_file):
    result = generate_dpi_definition(simple_func)
    check_file(result, "test_generate_dpi_header.sv")
    result = generate_dpi_definition(simple_func, pretty_print=False)
    assert result == 'import "DPI-C" function int simple_func(input int a, input int b, input int c);'


if __name__ == "__main__":
    test_generate_c_header()

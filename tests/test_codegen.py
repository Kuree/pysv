from pysv import sv, DataType, Reference, import_
from pysv.codegen import (get_python_src, generate_cxx_function, generate_c_header, generate_pybind_code,
                          generate_sv_binding, generate_cxx_binding, generate_dpi_signature, generate_pybind_function)
# all the module imports in this file should be local to avoid breaking assertions


def test_get_dpi_definition():
    @sv(a=DataType.String, b=DataType.Byte, return_type=DataType.Object)
    def func(a, b):
        return a + b

    result = generate_dpi_signature(func)
    expected = 'import "DPI-C" function chandle func(input string a,\n' \
               '                                     input byte b);'
    assert result == expected

    result = generate_dpi_signature(func, pretty_print=False)
    expected = 'import "DPI-C" function chandle func(input string a, input byte b);' # noqa
    assert expected == result


def test_get_python_src():
    @sv()
    def func(a, b):
        return a + b

    result = get_python_src(func)
    expected = """def func(a, b):
    return a + b

__result = func(__a, __b)
"""
    assert result == expected


@sv()
def simple_func(a, b, c):
    return a + b - c


def test_generate_cxx_function(check_file):
    result = generate_cxx_function(simple_func, add_sys_path=False, add_class=False)
    check_file(result, "test_generate_cxx_function.cc")


def test_generate_c_header():
    result = generate_c_header(simple_func, pretty_print=False)
    assert result == "int32_t simple_func(int32_t a, int32_t b, int32_t c);"


def test_generate_cxx_code(check_file):
    result = generate_pybind_code([simple_func])
    check_file(result, "test_generate_cxx_code.cc")


def test_generate_bootstrap_restores_simulator_python_env(monkeypatch):
    import pysv.codegen as codegen

    monkeypatch.setattr(codegen, "is_conda", lambda: True)
    monkeypatch.setattr(codegen.sys, "prefix", "/opt/conda/envs/pysv")
    monkeypatch.setattr(codegen.sys, "base_prefix", "/opt/conda")
    monkeypatch.setattr(codegen.sys, "path", ["/project", "/opt/conda/envs/pysv/lib/python3.10"])

    result = codegen.generate_bootstrap_code(add_sys_path=True, add_class=False, add_imports=False,
                                             add_local_object=False)

    assert 'std::string conda_python_home = "/opt/conda/envs/pysv";' in result
    assert 'bool has_python_env_vars = !python_env_vars.first.empty() || !python_env_vars.second.empty();' in result
    assert "set_py_env(std::make_pair(conda_python_home, conda_python_path));" in result
    assert "if (has_python_env_vars) {" in result


def test_generate_dpi_header(check_file):
    result = generate_dpi_signature(simple_func)
    check_file(result, "test_generate_dpi_header.sv")
    result = generate_dpi_signature(simple_func, pretty_print=False)
    assert result == 'import "DPI-C" function int simple_func(input int a, input int b, input int c);'

    @import_
    def simple_func_import(a, b):
        pass
    result = generate_dpi_signature(simple_func_import, pretty_print=False)
    assert result == 'export "DPI-C" function simple_func_import;'


def test_generate_array_dpi_header():
    @sv(a=DataType.IntArray[2])
    def array_2d(a):
        pass

    @sv(a=DataType.IntArray)
    def array_1d(a):
        pass

    result = generate_dpi_signature(array_2d, pretty_print=False)
    assert result == 'import "DPI-C" function void array_2d(input int a[][]);'
    result = generate_c_header(array_2d, pretty_print=False)
    assert result == "void array_2d(svOpenArrayHandle a);"

    result = generate_dpi_signature(array_1d, pretty_print=False)
    assert result == 'import "DPI-C" function void array_1d(input int a[]);'


def test_generate_context_dpi_header():
    @import_
    def echo(a):
        pass

    @sv(return_type=DataType.Int)
    def call_echo():
        return echo(41)

    result = generate_dpi_signature(call_echo, pretty_print=False)
    assert result == 'import "DPI-C" context function int call_echo();'


class SomeClass:
    def __init__(self):
        self.value = "hello world\n"

    @sv(return_type=DataType.Void)
    def print_a(self):
        print(self.value)

    @sv(return_type=DataType.Void)
    def print_b(self, num):
        print(self.value * num)

    @sv()
    def plus(self, num):
        return num + 1
    
    @sv(a=DataType.UInt, b=DataType.UInt, return_type=Reference(res_add=DataType.UInt, res_sub=DataType.UInt))
    def add_sub(self, a, b):
        return (a+b, a-b)


def test_generate_sv_binding(check_file):
    result = generate_sv_binding([SomeClass])
    check_file(result, "test_generate_sv_binding.sv")


def test_generate_cxx_binding(check_file):
    result = generate_cxx_binding([SomeClass])
    check_file(result, "test_generate_cxx_binding.cc")


def test_generate_cxx_code_class(check_file):
    result = generate_pybind_code([SomeClass])
    check_file(result, "test_generate_cxx_code_class.cc")


def test_generate_pybind_function():
    @import_
    def simple_func_import(a, b):
        pass
    result = generate_pybind_function([simple_func_import], pretty_print=False)
    assert result == 'm.def("simple_func_import", &simple_func_import);'


if __name__ == "__main__":
    test_generate_pybind_function()

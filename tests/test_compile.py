from pysv import compile_lib, sv, DataType, Reference
import os
from pysv.compile import compile_and_run


def test_compile(temp):
    @sv()
    def add(a, b):
        return a + b

    lib_file = compile_lib([add], cwd=temp)
    assert os.path.exists(lib_file)


def test_str(temp):
    @sv(s=DataType.String, return_type=DataType.String)
    def mul_str(num, s):
        return num * s

    lib_file = compile_lib([mul_str], cwd=temp)
    code = """
    const char *str = "test ";
    int32_t repeat = 4;
    auto r1 = mul_str(repeat, str);
    std::cout << r1 << std::endl;
    // another call
    auto r2 = mul_str(repeat + 1, str);
    std::cout << r2;
    """

    outputs = compile_and_run(lib_file, code, temp, [mul_str])
    outputs = outputs.splitlines()
    assert outputs[0] == "test " * 4
    assert outputs[1] == "test " * (4 + 1)


def test_numpy(temp):
    import numpy as np

    @sv()
    def min_(a, b):
        return np.min([a, b])

    lib_file = compile_lib([min_], cwd=temp)
    call_str = min_.make_call(-1, -2).str()
    code = """
    auto r = {0};
    std::cout << r << std::endl;
    """.format(call_str)

    outputs = compile_and_run(lib_file, code, temp, [min_])
    assert int(outputs) == -2


def test_empty_global(temp):
    @sv()
    def foo():
        pass

    foo.func_def.imports = {}
    compile_lib([foo], cwd=temp)


def test_type_import(temp):
    from random import Random

    @sv()
    def foo():
        rand = Random()
        rand.seed(0)
        val = rand.randint(0, 42)
        print(val)

    lib_file = compile_lib([foo], cwd=temp)
    call_str = foo.make_call().str() + ";\n"
    value = compile_and_run(lib_file, call_str, temp, [foo])
    value = int(value)
    rand = Random()
    rand.seed(0)
    expected = rand.randint(0, 42)
    assert value == expected


def test_no_call_sv_compile(temp):
    from pysv.codegen import generate_cxx_binding, generate_sv_binding

    @sv
    def foo():
        pass

    compile_lib([foo], cwd=temp)
    generate_cxx_binding([foo], filename=os.path.join(temp, "test.hh"))
    generate_sv_binding([foo], filename=os.path.join(temp, "test.svh"))


def test_function_import(temp):
    from random import randint

    @sv()
    def rand_():
        print(randint(0, 42))

    lib_file = compile_lib([rand_], cwd=temp)
    call_str = rand_.make_call().str() + ";\n"
    value = compile_and_run(lib_file, call_str, temp, [rand_])
    value = int(value)
    # randint is [a, b]
    assert value in range(0, 42 + 1)


def test_cxx_object_funcs_1(temp):
    class ClassA:
        @sv()
        def __init__(self):
            self.num = 21

    class ClassB:
        @sv(a=DataType.Object)
        def __init__(self, a):
            self.a = a

        @sv(return_type=ClassA)
        def create_a(self, num):
            a = ClassA()
            a.num = num
            return a

        @sv(a=ClassA)
        def add(self, a):
            return self.a.num + a.num

    lib_file = compile_lib([ClassA, ClassB], cwd=temp)
    cxx_code = """
using namespace pysv;
ClassA a1;
ClassB b(&a1);
ClassA a2 = b.create_a(-42);
std::cout << b.add(&a1) << std::endl;
std::cout << b.add(&a2);
pysv_finalize();
        """
    values = compile_and_run(lib_file, cxx_code, temp, [ClassA, ClassB], use_implementation=True).split("\n")
    assert int(values[0]) == 42
    assert int(values[1]) == (21 - 42)


def test_cxx_object_funcs_2(temp):
    class ClassA2:
        @sv()
        def __init__(self):
            self.num = 42

    @sv(a=ClassA2)
    def foo(a):
        print(a.num)

    lib_file = compile_lib([ClassA2, foo], cwd=temp)
    cxx_code = """
using namespace pysv;
ClassA2 a;
foo(&a);
pysv_finalize();
    """
    value = compile_and_run(lib_file, cxx_code, temp, [ClassA2, foo], use_implementation=True)
    value = int(value)
    assert value == 42


def test_function_output_ref1(temp):
    @sv(return_type=Reference(a=DataType.Int))
    def func_output():
        return 42

    lib_file = compile_lib([func_output], cwd=temp)
    cxx_code = """
using namespace pysv;
int a;
func_output(&a);
printf("%d", a);
pysv_finalize();
"""
    value = compile_and_run(lib_file, cxx_code, temp, [func_output], use_implementation=True)
    value = int(value)
    assert value == 42


def test_function_output_ref2(temp):
    @sv(return_type=Reference(a=DataType.Int, b=DataType.Int))
    def func_output():
        return 42, 43

    lib_file = compile_lib([func_output], cwd=temp)
    cxx_code = """
using namespace pysv;
int a, b;
func_output(&a, &b);
printf("%d\\n%d", a, b);
pysv_finalize();
"""
    value = compile_and_run(lib_file, cxx_code, temp, [func_output], use_implementation=True)
    values = [int(v) for v in value.split()]
    assert values[0] == 42 and values[1] == 43;


if __name__ == "__main__":
    test_function_output_ref2("temp")

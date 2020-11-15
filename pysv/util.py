import subprocess
import os
from pysv import generate_c_header
import shutil


def get_cxx_headers(func_defs):
    headers = []
    for func_def in func_defs:
        headers.append(generate_c_header(func_def))
    result = "#include <iostream>\n"
    result += 'extern "C" {\n'
    result += "\n".join(headers)
    result += "\n}\n"
    return result


def __get_cxx_compiler():   # pragma: no cover
    # TODO: this will not work for windows, since in most of the time
    #   it requires msvc and a project file. consider change the compilation
    #   flow into CMake
    if shutil.which("c++") is not None:
        return "c++"
    elif shutil.which("g++") is not None:
        return "g++"
    elif shutil.which("clang++") is not None:
        return "clang++"
    else:
        raise ValueError("Unable to find C++ compiler")


def compile_and_run(lib_path, cxx_content, cwd, func_defs, extra_headers=""):
    """Used for testing or simple C++ code. Returns captured stdout"""
    headers = get_cxx_headers(func_defs)
    headers += "\n" + extra_headers + "\n"
    # write out the file
    filename = os.path.join(cwd, "test_cxx.cc")
    with open(filename, "w+") as f:
        f.write(headers)
        f.write("\n")
        f.write("int main() {\n")
        f.write(cxx_content)
        f.write("\nreturn 0;\n}")
    # need to figure out the system CXX compiler
    # this is not portable but good enough
    cxx = __get_cxx_compiler()
    args = [cxx, filename, lib_path, "-o", os.path.join(cwd, "test_cxx"), "-std=c++11"]
    print(" ".join(args))
    subprocess.check_call(args)
    env = os.environ.copy()
    output = subprocess.check_output(os.path.join(cwd, "test_cxx"), env=env)
    output = output.decode("utf-8")
    return output


def simply_dpi_call_compile(dpi_call):
    result = dpi_call.func_def.func_name
    arg_values = []
    args = dpi_call.args
    for arg in args:
        arg_values.append(str(arg))
    result += "(" + ", ".join(arg_values) + ")"

    return result

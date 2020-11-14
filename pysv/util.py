import subprocess
import os
from pysv import generate_c_header


def get_cxx_headers(func_defs):
    headers = []
    for func_def in func_defs:
        headers.append(generate_c_header(func_def))
    result = "#include <iostream>\n"
    result += 'extern "C" {'
    result += "\n".join(headers)
    result += "}\n"
    return result


def compile_and_run(lib_path, cxx_content, cwd, func_defs, extra_headers=""):
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
    args = ["g++", filename, lib_path, "-o", os.path.join(cwd, "test_cxx")]
    print(" ".join(args))
    subprocess.check_call(args)
    env = os.environ.copy()
    output = subprocess.check_output(os.path.join(cwd, "test_cxx"), env=env)
    output = output.decode("utf-8")
    return output

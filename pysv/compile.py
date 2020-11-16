from .codegen import generate_cxx_code, generate_cxx_headers
import subprocess
import os
import shutil
import platform


def compile_lib(func_defs, cwd, lib_name="pysv", pretty_print=True, release_build=False):
    if not os.path.isdir(cwd):
        os.makedirs(cwd, exist_ok=True)
    # need to copy stuff over
    root_dir = os.path.dirname(__file__)
    pybind_path = os.path.join(root_dir, "extern", "pybind11")
    assert os.path.isdir(pybind_path)
    # copy that to cwd if it doesn't exist
    pybind_path_dst = os.path.join(cwd, "pybind11")
    if not os.path.isdir(pybind_path_dst):
        shutil.copytree(pybind_path, pybind_path_dst)
    # find the cmake file
    cmake_file = os.path.join(root_dir, "CMakeLists.txt")
    shutil.copyfile(cmake_file, os.path.join(cwd, "CMakeLists.txt"))

    # codegen the target
    src = generate_cxx_code(func_defs, pretty_print)
    output_filename = os.path.join(cwd, "{0}.cc".format(lib_name))
    skip_write_out = False
    if os.path.exists(output_filename):
        with open(output_filename) as f:
            content = f.read()
            if content == src:
                skip_write_out = True
    if not skip_write_out:
        with open(os.path.join(cwd, "{0}.cc".format(lib_name)), "w+") as f:
            f.write(src)

    # need to run cmake command
    build_dir = os.path.join(cwd, "build")
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    cmake_args = ["-DTARGET=" + lib_name]
    if platform.system() != "Windows":
        if release_build:
            build_type = "Release"
        else:
            build_type = "Debug"
        cmake_args.append("-DCMAKE_BUILD_TYPE=" + build_type)
    subprocess.check_call(["cmake"] + cmake_args + [".."],
                          cwd=build_dir)
    # built it!
    # use platform default builder
    subprocess.check_call(["cmake", "--build", "."], cwd=build_dir)

    # make sure the actual so file exists
    if platform.system() == "Darwin":
        shared_lib_ext = ".dylib"
    else:
        shared_lib_ext = ".so"
    lib_file = os.path.join(build_dir, lib_name + shared_lib_ext)
    if not os.path.isfile(lib_file):
        raise FileNotFoundError("Not able to compile " + lib_file)
    return lib_file


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
    headers = generate_cxx_headers(func_defs)
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
    args = [cxx, filename, lib_path, f"-Wl,-rpath,{os.path.dirname(lib_path)}",
            "-o", os.path.join(cwd, "test_cxx")]
    print(" ".join(args))
    subprocess.check_call(args)
    env = os.environ.copy()
    output = subprocess.check_output(os.path.join(cwd, "test_cxx"), env=env)
    output = output.decode("utf-8")
    return output


def simply_dpi_call_compile(dpi_call, *args):
    result = dpi_call.func_def.func_name
    arg_values = []
    for arg in args:
        arg_values.append(str(arg))
    result += "(" + ", ".join(arg_values) + ")"

    return result

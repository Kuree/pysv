from .codegen import generate_pybind_code, generate_c_headers, generate_cxx_binding
import subprocess
import os
import shutil
import platform
import filecmp


def compile_lib(func_defs, cwd, lib_name="pysv", pretty_print=True, release_build=False, clean_up_build=False,
                add_sys_path=False):
    """
    Compile the python code into a shared library.
    if your simulator ships with its own Python distribution, e.g. Vivado simulator, you
    need to set this to True, otherwise leave it as is and pysv will figure it out
    """
    if not os.path.isdir(cwd):
        os.makedirs(cwd, exist_ok=True)
    # notice that fo follow the "lib" + name convention so the linker can find the library easily
    if len(lib_name) < 3 or lib_name[:3] != "lib":
        lib_name = "lib" + lib_name

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
    # if cmake exists and file are the same, don't do the copying
    dst_cmake = os.path.join(cwd, "CMakeLists.txt")
    if not (os.path.exists(dst_cmake) and filecmp.cmp(cmake_file, dst_cmake)):
        shutil.copyfile(cmake_file, dst_cmake)

    # codegen the target
    src = generate_pybind_code(func_defs, pretty_print, add_sys_path=add_sys_path)
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
    shared_lib_ext = ".so"
    lib_file = os.path.join(build_dir, lib_name + shared_lib_ext)
    if not os.path.isfile(lib_file):
        raise FileNotFoundError("Not able to compile " + lib_file)

    # need to move the lib_file to the parent cwd folder
    dst_lib_file = os.path.join(cwd, os.path.basename(lib_file))
    shutil.copy(lib_file, dst_lib_file)
    lib_file = dst_lib_file
    assert os.path.isfile(lib_file)

    if clean_up_build:
        shutil.rmtree(build_dir, ignore_errors=True)

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


def compile_and_run(lib_path, cxx_content, cwd, func_defs, extra_headers="", use_implementation=False):
    """Used for testing or simple C++ code. Returns captured stdout"""
    if use_implementation:
        headers = generate_cxx_binding(func_defs)
    else:
        headers = generate_c_headers(func_defs)
    headers += "\n" + extra_headers + "\n"
    # write out the file
    filename = os.path.join(cwd, "test_cxx.cc")
    with open(filename, "w+") as f:
        f.write(headers)
        f.write("\n")
        f.write("int main() {\n")
        f.write(cxx_content)
        f.write("pysv_finalize();\n")
        f.write("\nreturn 0;\n}")
    # need to figure out the system CXX compiler
    # this is not portable but good enough
    cxx = __get_cxx_compiler()
    args = [cxx, filename, lib_path, f"-Wl,-rpath,{os.path.dirname(lib_path)}",
            "-o", os.path.join(cwd, "test_cxx"), "-std=c++11"]
    print(" ".join(args))
    subprocess.check_call(args)
    env = os.environ.copy()
    output = subprocess.check_output(os.path.join(cwd, "test_cxx"), env=env)
    output = output.decode("utf-8")
    return output

from .codegen import generate_cxx_code
import subprocess
import os
import shutil


def compile_lib(func_defs, cwd, lib_name="pysv", pretty_print=True):
    if not os.path.isdir(cwd):
        os.makedirs(cwd, exist_ok=True)
    # need to copy stuff over
    root_dir = os.path.dirname(os.path.dirname(__file__))
    pybind_path = os.path.join(root_dir, "extern", "pybind11")
    assert os.path.isdir(pybind_path)
    # copy that to cwd if it doesn't exist
    pybind_path_dst = os.path.join(cwd, "pybind11")
    if not os.path.isdir(pybind_path_dst):
        shutil.copytree(pybind_path, pybind_path_dst)
    # find the cmake file
    cmake_file = os.path.join(root_dir, "pysv", "CMakeLists.txt")
    shutil.copyfile(cmake_file, os.path.join(cwd, "CMakeLists.txt"))

    # codegen the target
    src = generate_cxx_code(func_defs, pretty_print)
    with open(os.path.join(cwd, "{0}.cc".format(lib_name)), "w+") as f:
        f.write(src)

    # need to run cmake command
    build_dir = os.path.join(cwd, "build")
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    subprocess.check_call(["cmake", "-DTARGET=" + lib_name, ".."],
                          cwd=build_dir)
    # built it!
    subprocess.check_call(["make"], cwd=build_dir)

    # make sure the actual so file exists
    so_file = os.path.join(build_dir, lib_name + ".so")
    if not os.path.isfile(so_file):
        raise FileNotFoundError("Not able to compile " + so_file)
    return so_file

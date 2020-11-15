from .codegen import generate_cxx_code
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
    so_file = os.path.join(build_dir, lib_name + ".so")
    if not os.path.isfile(so_file):
        raise FileNotFoundError("Not able to compile " + so_file)
    return so_file

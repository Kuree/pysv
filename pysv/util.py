import sys
import shutil
import subprocess
import os
import abc


def should_add_class(func_defs):
    for func_def in func_defs:
        if type(func_def) == type:
            return True
    return False


def should_add_sys_path(func_defs):
    # looking into the imported module and see if they are system module
    defs = []
    for func_def in func_defs:
        if type(func_def) == type:
            # just need to get the constructor
            defs.append(func_def.__init__)
        else:
            defs.append(func_def)
    built_in_modules = sys.builtin_module_names
    for func_def in defs:
        for module_name in func_def.imports.values():
            if module_name not in built_in_modules:
                return True
    return False


def is_xcelium_available():
    return shutil.which("xrun") is not None


def is_vcs_available():
    return shutil.which("vcs") is not None


def is_questa_available():
    return shutil.which("vlog")


def is_vivado_available():
    return shutil.which("xsim")


def is_verilator_available():
    return shutil.which("verilator") is not None


# simple CAD tool runners
class Tester:
    def __init__(self, lib_path, *files: str, cwd=None, clean_up_run=False):
        self.lib_path = lib_path
        self.files = []
        for file in files:
            self.files.append(os.path.abspath(file))
        self.cwd = self._process_cwd(cwd)
        self.clean_up_run = clean_up_run
        self.__process = []

    @abc.abstractmethod
    def run(self, blocking=False):
        pass

    def _process_cwd(self, cwd):
        if cwd is None:
            cwd = "build"
        if not os.path.isdir(cwd):
            os.makedirs(cwd, exist_ok=True)
        # copy files over
        files = []
        for file in self.files:
            new_filename = os.path.abspath(os.path.join(cwd, os.path.basename(file)))
            if new_filename != file:
                if os.path.isfile(new_filename):
                    os.remove(new_filename)
                shutil.copyfile(file, new_filename)
            ext = os.path.splitext(new_filename)[-1]
            if ext != ".h" and ext != ".hh":
                files.append(new_filename)
        self.files = files
        return cwd

    def _set_lib_env(self):
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = os.path.dirname(os.path.abspath(self.lib_path))
        return env

    def _run(self, args, cwd, env, blocking):
        if blocking:
            subprocess.check_call(args, cwd=cwd, env=env)
        else:
            p = subprocess.Popen(args, cwd=cwd, env=env)
            self.__process.append(p)

    def clean_up(self):
        if self.clean_up_run and os.path.exists(self.cwd) and os.path.isdir(
                self.cwd):
            shutil.rmtree(self.cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()
        for p in self.__process:
            p.kill()

    def __enter__(self):
        return self


class VerilatorTester(Tester):
    def __init__(self, lib_path, *files: str, cwd=None, clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)

    def run(self, blocking=True):
        # compile it first
        verilator = shutil.which("verilator")
        args = [verilator, "--cc", "--exe"]
        args += self.files + [os.path.abspath(self.lib_path), "-Wno-fatal"]
        subprocess.check_call(args, cwd=self.cwd)
        # symbolic link it first
        env = self._set_lib_env()

        # find the shortest file
        # automatic detect the makefile
        mk_file = ""
        for f in self.files:
            name, ext = os.path.splitext(os.path.basename(f))
            if ext == ".sv" or ext == ".v":
                mk_file = "V" + name + ".mk"
                break
        assert len(mk_file) > 0, "Unable to find any makefile from Verilator"
        # make the file
        subprocess.check_call(["make", "-C", "obj_dir", "-f", mk_file],
                              cwd=self.cwd, env=env)
        # run the application
        name = os.path.join("obj_dir", mk_file.replace(".mk", ""))
        self._run([name], self.cwd, env, blocking)


class CadenceTester(Tester):
    def __init__(self, lib_path, *files: str, cwd=None, clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)
        self.toolchain = ""
        self.lib_path = os.path.relpath(self.lib_path, cwd)

    def run(self, blocking=True):
        assert len(self.toolchain) > 0
        env = self._set_lib_env()
        # run it
        args = [self.toolchain] + list(self.files) + self.__get_flag()
        self._run(args, self.cwd, env, blocking)

    def __get_flag(self):
        return ["-sv_lib", self.lib_path]


class XceliumTester(CadenceTester):
    def __init__(self, lib_path, *files: str, cwd=None, clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)
        self.toolchain = "xrun"


class VCSTester(Tester):
    def __init__(self, lib_path, *files: str, cwd=None, clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)

    def run(self, blocking=True):
        env = self._set_lib_env()
        # run it
        args = ["vcs"] + list(self.files) + self.__get_flag()
        self._run(args, self.cwd, env, True)
        # run the simv
        self._run(["./simv"], self.cwd, env, blocking)

    def __get_flag(self):
        return ["-sv_lib", self.lib_path, "-sverilog"]


class QuestaTester(Tester):
    def __init__(self, lib_path, *files: str, cwd=None, top_name="top", clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)
        self.top_name = top_name
        self.lib_path = os.path.relpath(self.lib_path, cwd)

    def run(self, blocking=True):
        env = self._set_lib_env()
        args = ["vlog"] + list(self.files)
        self._run(args, self.cwd, env, True)
        # run vsim command
        args = ["vsim", self.top_name] + self.__get_flag()
        self._run(args, self.cwd, env, blocking)

    def __get_flag(self):
        name = os.path.splitext(self.lib_path)[0]
        return ["-sv_lib", name, "-batch", "-do",  "run -all; exit"]


class VivadoTester(Tester):
    def __init__(self, lib_path, *files: str, cwd=None, top_name="top", clean_up_run=False):
        super().__init__(lib_path, *files, cwd=cwd, clean_up_run=clean_up_run)
        self.top_name = top_name
        self.lib_path = os.path.relpath(self.lib_path, cwd)

    def run(self, blocking=True):
        env = self._set_lib_env()
        args = ["xvlog", "--sv"] + self.files
        self._run(args, self.cwd, env, True)
        lib_name = os.path.splitext(self.lib_path)[0]
        args = ["xelab", "--sv_lib", lib_name, self.top_name]
        self._run(args, self.cwd, env, True)
        args = ["xsim", "-R", self.top_name]
        self._run(args, self.cwd, env, blocking)

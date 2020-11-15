import inspect
import astor
import ast
import types
import textwrap
from .function import dpi, DPIFunctionCall, Function
from .types import DataType
from .frame import _inspect_frame


class __ArgNameVisitor(ast.NodeVisitor):
    def __init__(self):
        self.arg_names = []

    def visit_arg(self, node: ast.arg):
        self.arg_names.append(node.arg)
        self.generic_visit(node)


def get_func_args(src):
    class_tree = ast.parse(textwrap.dedent(src))
    assert isinstance(class_tree.body[0], ast.FunctionDef)
    args = class_tree.body[0].args
    visitor = __ArgNameVisitor()
    visitor.visit(args)
    return visitor.arg_names


class PySVModel(Function):
    def __init__(self):
        super().__init__()
        # need to figure out the args and arg names
        self.imports = _inspect_frame()
        frame = inspect.currentframe().f_back
        code = inspect.getsource(frame.f_code)
        signatures = get_func_args(code)
        local_vars = frame.f_locals
        # decide types here
        self.arg_names = []
        self.arg_types = {}
        self.self_arg_name = "self"
        for idx, arg_name in enumerate(signatures):
            arg = local_vars[arg_name]
            if idx == 0:
                assert isinstance(arg, PySVModel)
                # change it to handle object
                t = DataType.CHandle
                self.self_arg_name = arg_name
            else:
                if isinstance(arg, str):
                    t = DataType.String
                elif isinstance(arg, int):
                    t = DataType.Int
                elif isinstance(arg, object):
                    t = DataType.CHandle
                else:
                    raise ValueError("Unable to convert {0}({1}) to C types".format(arg_name, arg))
            self.arg_names.append(arg_name)
            self.arg_types[arg_name] = t

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, name)
        if isinstance(obj, DPIFunctionCall):
            func_def = obj.func_def
            if func_def.parent_class is not None:
                assert func_def.parent_class == self.__class__
            else:
                func_def.parent_class = self.__class__
        return obj

    class __HasDPIVisitor(ast.NodeVisitor):
        def __init__(self):
            self.result = False

        def visit_Name(self, node: ast.Name):
            if node.id == "dpi" or node.id == dpi.__name__:
                self.result = True
            self.generic_visit(node)

    @staticmethod
    def __has_dpi_deco(node):
        visitor = PySVModel.__HasDPIVisitor()
        visitor.visit(node)
        return visitor.result

    def get_func_src(self):
        # we need to remove all the @dpi decorators in the ast
        # so that they can actually be called
        code = inspect.getsource(self.__class__)
        class_tree = ast.parse(textwrap.dedent(code))
        # need to clear out any DPI function decorator
        class_ast = class_tree.body[0]
        assert isinstance(class_ast, ast.ClassDef)
        class_body = class_ast.body
        for ast_block in class_body:
            if isinstance(ast_block, ast.FunctionDef):
                ast_block.decorator_list = [node for node in ast_block.decorator_list if not self.__has_dpi_deco(node)]

        src = astor.to_source(class_tree)
        return src

    @property
    def func_name(self):
        # hardcode the func name
        return self.__class__.__name__ + "__init__"

    @dpi(return_type=DataType.Void)
    def destroy(self):
        # actual implementation provided by the codegen
        pass

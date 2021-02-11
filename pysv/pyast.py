import ast
import astor
import inspect
import textwrap
import typing


class __HasDPIVisitor(ast.NodeVisitor):
    def __init__(self):
        self.result = False

    def visit_Name(self, node: ast.Name):
        if node.id == "sv":
            self.result = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr == "sv":
            self.result = True
        self.generic_visit(node)


class __HasReturnVisitor(ast.NodeVisitor):
    def __init__(self):
        self.result = False

    def visit_Return(self, node: ast.Return):
        self.result = True


def has_sv_deco(node):
    visitor = __HasDPIVisitor()
    visitor.visit(node)
    return visitor.result


def has_return(func: typing.Callable):
    fn_src = inspect.getsource(func)
    func_tree = ast.parse(textwrap.dedent(fn_src))
    fn_body = func_tree.body[0]
    visitor = __HasReturnVisitor()
    visitor.visit(fn_body)
    return visitor.result


def get_class_src(cls: type):
    # we need to remove all the @dpi decorators in the ast
    # so that they can actually be called
    if hasattr(cls, "_source_code_"):
        # If we define a class inside exec (e.g. when doing AST rewrites on the
        # Python source) we can't use inspect.getsource (since the code comes
        # froms a string rather than a file).  So, we provide a special
        # attribute that downstream tools can use to store the generated source
        # code
        code = cls._source_code_
    else:
        code = inspect.getsource(cls)
    class_tree = ast.parse(textwrap.dedent(code))
    # need to clear out any DPI function decorator
    class_ast = class_tree.body[0]
    assert isinstance(class_ast, ast.ClassDef)
    class_body = class_ast.body
    for ast_block in class_body:
        if isinstance(ast_block, ast.FunctionDef):
            ast_block.decorator_list = [node for node in ast_block.decorator_list if not has_sv_deco(node)]

    src = astor.to_source(class_tree)
    return src


def get_function_src(func: type, check_decorator=True):
    fn_src = inspect.getsource(func)
    if not check_decorator:
        return fn_src
    func_tree = ast.parse(textwrap.dedent(fn_src))
    fn_body = func_tree.body[0]
    # only support one decorator
    assert len(fn_body.decorator_list) == 1, "Only dpi decorator is supported"
    # remove the decorator
    fn_body.decorator_list = []
    src = astor.to_source(fn_body)
    return src

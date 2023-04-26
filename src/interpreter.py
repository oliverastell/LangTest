from src.parse import Nil, underline_char, colorama, Bool, Token
from src.parsetokens import Value

##########################################
##                                      ##
##  AST VISITORS                        ##
##                                      ##
##########################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        self.error(f'No visit_{type(node).__name__} method')

##########################################
##                                      ##
##  Interpreter                         ##
##                                      ##
##########################################

class Interpreter(NodeVisitor):
    def __init__(self, tree) -> None:
        self.tree = tree

    def get_scope(self):
        if len(self.scope_stack) == 0: return None
        return self.scope_stack[-1]

    def get_global_scope(self):
        if len(self.scope_stack) == 0: return None
        return self.scope_stack[0]

    def operate(self, op: str, x, y = None):
        if y != None:

            if hasattr(x, "op_" + op):
                return getattr(x, "op_" + op)(y)
            elif op == "EQUALS":
                return Bool(y) 
            elif op == "EQUALSE":
                return x == y
            elif op == "BANGE":
                return x != y
            elif op == "LESSER":
                return x < y
            elif op == "LESSERE":
                return x <= y
            elif op == "GREATER":
                return x > y
            elif op == "GREATERE":
                return x >= y
            elif op == "OR":
                return x or y
            elif op == "AND":
                return x and y
            else:
                self.error(f"Invalid operation {type(x).__name__} {op} {type(y).__name__}")
        else:
            if op == "PLUS":
                if hasattr(x, "op_POS"):
                    return getattr(x, "op_POS")()
            elif op == "MINUS":
                if hasattr(x, "op_NEG"):
                    return getattr(x, "op_NEG")()
            elif op == "NOT":
                if hasattr(x, "op_NOT"):
                    return getattr(x, "op_NOT")()
            else:
                self.error(f"Invalid operation {op} {type(x).__name__}")

    def error(self, reason, oindex: int = 0):
        print(f"\n{colorama.Fore.RED}{underline_char}Interpreting Error <OI {oindex}>{colorama.Style.RESET_ALL}{colorama.Fore.CYAN}{colorama.Style.RESET_ALL}\n{reason}\n")
        exit()

    def visit_Call(self, node):
        params = []
        for parameter in node.parameters.values:
            params.append(self.visit(parameter))

        return self.visit(self.visit(node.left).call(params))

    def visit_BinOp(self, node):
        return self.operate(node.op.type, self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        return self.operate(node.op.type, self.visit(node.expr))

    def visit_Scope(self, node):
        node.init_vars()
        self.scope_stack.append(node)
        for statement in node.statements:
            val = Nil()
            if type(statement).__name__ == "Return":
                val = self.visit(statement.token)
                break
            self.visit(statement)
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            node.vars = None
        else:
            self.global_scope = self.scope_stack[0]
            del self.scope_stack
        return val

    def visit_If(self, node):
        val = self.visit(node.condition)
        if val.bool():
            return self.visit(node.result)
        return Nil()

    def visit_Error(self, node):
        self.error(node.token.token.value)

    def visit_Reassign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        before = self.get_scope().get_var(var_name)
        self.get_scope().set_var(var_name, self.operate(node.token.type, before, value))

        return value

    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        if not node.public:
            self.get_scope().set_var(var_name, value)
        else:
            self.get_scope().set_var(var_name, value)
            self.get_global_scope().set_var(var_name, value)
        return value

    def visit_Nil(self, _):
        return Nil()

    def visit_Var(self, node):
        var_name = node.value
        value = self.get_scope().get_var(var_name)
        if value != None:
            return value
        else:
            self.error(f"Invalid Variable: {var_name}")
    
    def visit_Function(self, node):
        return node

    def visit_String(self, node):
        return node

    def visit_Bool(self, node):
        return node

    def visit_Num(self, node):
        return node

    def interpret(self, file: str | list | tuple = ''):
        tree = self.tree
        if tree is None:
            return ''

        self.scope_stack = []
        return self.visit(tree)
    
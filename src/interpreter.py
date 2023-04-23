from src.parse import Nil, underline_char, colorama, Bool

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
        self.GLOBAL_MEMORY = {}

    def operate(self, op: str, x, y = None):
        if y != None:

            if hasattr(x, "op_" + op):
                return getattr(x, "op_" + op)(y)
            elif op == "EQUALS":
                return y
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
                self.error(f"Invalid operation {x} {op} {y}")
        else:
            if op == "PLUS":
                if hasattr(x, "op_POS"):
                    return getattr(x, "op_POS")()
            elif op == "MINUS":
                if hasattr(x, "op_NEG"):
                    return getattr(x, "op_NEG")()

    def error(self, reason):
        print(f"\n{colorama.Fore.RED}{underline_char}Interpreting Error{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{self.parser.filename}> {colorama.Style.RESET_ALL}\n{reason}\n")
        exit()

    def visit_BinOp(self, node):
        return self.operate(node.op.type, self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        return self.operate(node.op.type, self.visit(node.expr))

    def visit_Scope(self, node):
        for statement in node.statements:
            val = Nil()
            if type(statement).__name__ == "Return":
                val = self.visit(statement.token)
                break
            self.visit(statement)
        return val

    def visit_If(self, node):
        if self.visit(node.condition).bool():
            self.visit(node.result)

    def visit_Print(self, node):
        print(self.visit(node.token).repr())
        return Nil()

    def visit_Reassign(self, node):
        var_name = node.left.value
        op = node.op.type
        if var_name not in self.GLOBAL_MEMORY:
            self.error(f"Invalid Variable: {var_name}")
        value = self.operate(op, self.GLOBAL_MEMORY[var_name], self.visit(node.right))
        self.GLOBAL_MEMORY[var_name] = value
        return value

    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        self.GLOBAL_MEMORY[var_name] = value
        return value

    def visit_Nil(self, _):
        return Nil()

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_MEMORY.get(var_name)
        if val is None:
            self.error(f"Invalid Variable: {var_name}")
        else:
            return val

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

        return self.visit(tree)
    
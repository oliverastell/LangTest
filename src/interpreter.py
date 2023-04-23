
##########################################
##                                      ##
##  Interpreter                         ##
##                                      ##
##########################################

def operate(op: str, x, y: None):
    if y != None:
        if op == "PLUS":
            return x + y
        elif op == "MINUS":
            return x - y
        elif op == "MUL":
            return x * y
        elif op == "DIV":
            return x / y
        elif op == "EXP":
            return x ** y
        elif op == "MOD":
            return x % y
        elif op == "DIVDIV":
            return x // y
        elif op == "EQUALS":
            return y
    else:
        if op == "PLUS":
            return +x
        elif op == "MINUS":
            return -x


class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self, parser) -> None:
        self.parser = parser

    def visit_BinOp(self, node):
        return operate(node.op.type, self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        return operate(node.op.type, self.visit(node.left))

    def visit_Scope(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_Reassign(self, node):
        var_name = node.left.value
        op = node.op.type
        if var_name not in self.GLOBAL_SCOPE:
            raise NameError(repr(var_name))
        self.GLOBAL_SCOPE[var_name] = operate(op, self.GLOBAL_SCOPE[var_name], self.visit(node.right))

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_NoOp(self, node):
        pass

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_Num(self, node):
        return node.value

    def interpret(self, file: str | list | tuple = ''):
        tree = self.parser.parse(file)
        self.GLOBAL_SCOPE = {}

        return self.visit(tree)
    
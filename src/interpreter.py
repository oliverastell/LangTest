from src.parse import Nil, underline_char, colorama

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

def repr_float(x):
    if type(x) == float:
        if x.is_integer(): return str(int(x))
        else: return str(float(x))
    else:
        return repr(x)

class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        self.error(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self, parser) -> None:
        self.parser = parser

    def error(self, reason):
        print(f"\n{colorama.Fore.RED}{underline_char}Interpreting Error{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{self.parser.filename}>\n{reason}\n")
        exit()

    def visit_BinOp(self, node):
        return operate(node.op.type, self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        return operate(node.op.type, self.visit(node.token))

    def visit_Scope(self, node):
        for statement in node.statements:
            if type(statement).__name__ == "Return":
                val = statement.token
                break
                
            val = self.visit(statement)
        return val

    def visit_Print(self, node):
        print(repr_float(self.visit(node.token)))
        return Nil()

    def visit_Reassign(self, node):
        var_name = node.left.value
        op = node.op.type
        if var_name not in self.GLOBAL_SCOPE:
            self.error(f"Invalid Variable: {var_name}")
        value = operate(op, self.GLOBAL_SCOPE[var_name], self.visit(node.right))
        self.GLOBAL_SCOPE[var_name] = value
        return value

    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        self.GLOBAL_SCOPE[var_name] = value
        return value

    def visit_Nil(self, node):
        return Nil()

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            self.error(f"Invalid Variable: {var_name}")
        else:
            return val

    def visit_Num(self, node):
        return node.value

    def interpret(self, file: str | list | tuple = ''):
        tree = self.parser.parse(file)
        self.GLOBAL_SCOPE = {}

        return self.visit(tree)
    
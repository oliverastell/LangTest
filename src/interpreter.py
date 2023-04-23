from src.parse import Nil, underline_char, colorama, Bool, Token

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

class VarTable:
        def __init__(self, scope) -> None:
            self.table = {}
            self.scope = scope
        
        def get(self, interpreter, var):
            val = self.table.get(var)
            if val == None:
                return interpreter.scope_list[0].table.get(var)
            else: return val

        def assign(self, var, value):
            self.table[var] = value

        def reassign(self, interpreter, var, op, value):
            if self.get(interpreter, var) != None:
                self.table[var] = self.operate(op, self.table[var], value)
            else:
                interpreter.error(f"Invalid Variable: {var}")

class Interpreter(NodeVisitor):
    def __init__(self, tree) -> None:
        self.tree = tree

    def get_vartable(self):
        return self.scope_list[-1]

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
                self.error(f"Invalid operation {x} {op} {y}")
        else:
            if op == "PLUS":
                if hasattr(x, "op_POS"):
                    return getattr(x, "op_POS")()
            elif op == "MINUS":
                if hasattr(x, "op_NEG"):
                    return getattr(x, "op_NEG")()

    def error(self, reason):
        print(f"\n{colorama.Fore.RED}{underline_char}Interpreting Error{colorama.Style.RESET_ALL}{colorama.Fore.CYAN}{colorama.Style.RESET_ALL}\n{reason}\n")
        exit()

    def visit_BinOp(self, node):
        return self.operate(node.op.type, self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        return self.operate(node.op.type, self.visit(node.expr))

    def visit_Scope(self, node):
        self.scope_list.append(VarTable(node))
        for statement in node.statements:
            val = Nil()
            if type(statement).__name__ == "Return":
                val = self.visit(statement.token)
                break
            self.visit(statement)
        if len(self.scope_list) > 1:
            self.scope_list.pop()
        else:
            self.global_scope = self.scope_list[0]
            del self.scope_list
        return val

    def visit_If(self, node):
        val = self.visit(node.condition)
        if val.bool():
            self.visit(node.result)

    def visit_Print(self, node):
        print(self.visit(node.token).repr())
        return Nil()

    def visit_Reassign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        op = node.op.type
        self.get_vartable().reassign(self, op, var_name, value)
        return value

    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        if node.assignment_type == "LET":
            self.get_vartable().assign(var_name, value)
        elif node.assignment_type == "PUB":
            self.scope_list[0].assign(var_name, value)
        return value

    def visit_Nil(self, _):
        return Nil()

    def visit_Var(self, node):
        var_name = node.value
        value = self.get_vartable().get(self, var_name)
        if value != None:
            return value
        else:
            self.error(f"Invalid Variable: {var_name}")

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

        self.scope_list = []
        return self.visit(tree)
    

##########################################
##                                      ##
##  Interpreter                         ##
##                                      ##
##########################################

class NodeVisitor(object):
    def visit(self, node):
        if node == None:
            method_name = "visit_None"
        else:
            method_name = "visit_" + node.type
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        if node == None:
            raise Exception(f'No visit_None method')
        else:
            raise Exception(f'No visit_{node.type} method')

class Interpreter(NodeVisitor):
    def __init__(self, parser) -> None:
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == "PLUS":
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == "MINUS":
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == "MUL":
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == "DIV":
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == "EXP":
            return self.visit(node.left) ** self.visit(node.right)
        elif node.op.type == "MOD":
            return self.visit(node.left) % self.visit(node.right)
        elif node.op.type == "DIVDIV":
            return self.visit(node.left) // self.visit(node.right)

    def visit_UnaryOp(self, node):
        if node.op.type == "PLUS":
            return +self.visit(node.expr)
        elif node.op.type == "MINUS":
            return -self.visit(node.expr)

    def visit_NUMBER(self, node):
        return node.value

    def interpret(self, file: str | list | tuple = ''):
        tree = self.parser.parse(file)
        return self.visit(tree)
    
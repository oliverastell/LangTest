from src.lexer import Token

class AST:
    ...

class Value(AST):
    def op_EQUALS(self, other):
        val = other.value
        return Num(Token(other.token.type, val, other.token.oindex))
    def op_EQUALSE(self, other):
        val = self.value == other.value
        return Bool(Token("BOOL", val, self.token.oindex))
    def op_BANGE(self, other):
        val = self.value != other.value
        return Num(Token("BOOL", val, self.token.oindex))
    def op_LESSER(self, other):
        val = self.value < other.value
        return Num(Token("BOOL", val, self.token.oindex))
    def op_LESSERE(self, other):
        val = self.value <= other.value
        return Num(Token("BOOL", val, self.token.oindex))
    def op_GREATER(self, other):
        val = self.value > other.value
        return Num(Token("BOOL", val, self.token.oindex))
    def op_GREATERE(self, other):
        val = self.value >= other.value
        return Num(Token("BOOL", val, self.token.oindex))
    def op_OR(self, other):
        val = self.bool() or other.bool()
        return Num(Token("BOOL", val, self.token.oindex))
    def op_AND(self, other):
        val = self.bool() and other.bool()
        return Num(Token("BOOL", val, self.token.oindex))
    def bool(self):
        return True

class Scope(AST):
    def __init__(self, statements: list = None) -> None:
        if statements == None: statements = []
        self.statements = statements
    
    def __repr__(self) -> str:
        statements = []
        for s in self.statements:
            statements.append(repr(s))
        return f"Scope({', '.join(statements)})"

class If(AST):
    def __init__(self, condition, result) -> None:
        self.condition = condition
        self.result = result
    
    def __repr__(self) -> str:
        return f"If({self.condition}, {self.result})"

class Print(AST):
    def __init__(self, token) -> None:
        self.token = token
    
    def __repr__(self) -> str:
        return f"Print({self.token})"

class Return(AST):
    def __init__(self, token) -> None:
        self.token = token
    
    def __repr__(self) -> str:
        return f"Return({self.token})"

class Assign(AST):
    def __init__(self, left, op, right, assignment_type) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right
        self.assignment_type = assignment_type
    
    def __repr__(self) -> str:
        return f"Assign({self.left}, {self.op}, {self.right}, {self.assignment_type})"

class Reassign(AST):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def __repr__(self) -> str:
        return f"Reassign({self.left}, {self.op}, {self.right})"

class Var(AST):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value
    
    def __repr__(self) -> str:
        return f"Var({self.token})"

class String(Value):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value

    def repr(self) -> str:
        return self.value

    def bool(self) -> bool:
        return self.value != ''
    
    def op_PLUS(self, other):
        val = self.value + other.value
        return String(Token("STRING", val, self.token.oindex))

    def __repr__(self) -> str:
        return f"String({self.token})"

class Bool(Value):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value

    def repr(self) -> str:
        if self.value: return "true"
        return "false"

    def bool(self) -> bool:
        return self.value
    
    def __repr__(self) -> str:
        return f"Bool({self.token})"

class Num(Value):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value
    
    def repr(self) -> str:
        if self.value.is_integer(): return str(int(self.value))
        return str(self.value)
    
    def bool(self) -> bool:
        return self.value != 0
    
    def op_POS(self):
        val = +self.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def op_NEG(self):
        val = -self.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def op_PLUS(self, other):
        val = self.value + other.value
        return Num(Token("NUMBER", val, self.token.oindex))
    
    def op_MINUS(self, other):
        val = self.value - other.value
        return Num(Token("NUMBER", val, self.token.oindex))
    
    def op_MUL(self, other):
        val = self.value * other.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def op_DIV(self, other):
        val = self.value / other.value
        return Num(Token("NUMBER", val, self.token.oindex))
    
    def op_DIVDIV(self, other):
        val = self.value // other.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def op_MOD(self, other):
        val = self.value % other.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def op_EXP(self, other):
        val = self.value ** other.value
        return Num(Token("NUMBER", val, self.token.oindex))

    def __repr__(self) -> str:
        return f"Num({self.token})"

class Nil(Value):
    def __init__(self, oindex: int = 0) -> None:
        self.token = Token("NIL", None, oindex)
        self.value = None

    def repr(self) -> str:
        return "nil"
    
    def bool(self) -> bool:
        return False
    
    def __repr__(self) -> str:
        return f"Nil({self.token.oindex})"

class UnaryOp(AST):
    def __init__(self, op, expr) -> None:
        self.token = self.op = op
        self.expr = expr
    
    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.expr})"

class BinOp(AST):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.right = right
        self.op = op
    
    def __repr__(self) -> str:
        return f"BinOp({self.left}, {self.op.value}, {self.right})"
from src.lexer import Token, Tokenizer, colorama, underline_char

##########################################
##                                      ##
##  Parser                              ##
##                                      ##
##########################################

class AST:
    ...

class Scope(AST):
    def __init__(self, statements: list = []) -> None:
        self.statements = statements
    
    def __repr__(self) -> str:
        statements = []
        for s in self.statements:
            statements.append(str(s))
        return f"Scope({', '.join(statements)})"

class Assign(AST):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def __repr__(self) -> str:
        return f"Assign({self.left}, {self.op}, {self.right})"

class Reassign(AST):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value
    
    def __repr__(self) -> str:
        return f"Var({self.token})"

class Num(AST):
    def __init__(self, token) -> None:
        self.token = token
        self.value = token.value
    
    def __repr__(self) -> str:
        return str(self.value)

class NoOp(AST):
    def __repr__(self) -> str:
        return "NoOp"

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

class Parser:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer
    
    def error(self, reason: str):
        read = '\n' + self.tokenizer.source[:self.tok.oindex + 1]
        
        read_row = read[read.rfind('\n'):][1:]
        line = read.count('\n')
        full_row = self.tokenizer.source.split('\n')[line - 1]

        if type(self.filename) in (list, tuple):
            filename = self.filename[-1]
        elif type(self.filename) == str:
            filename = self.filename

        arrows = ' '*(len(read_row) - 1) + '^' * len(str(self.tok.value))

        print(f"\n{colorama.Fore.RED}{underline_char}AN ERROR OCCURED{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{filename}>: Line {line}{colorama.Style.RESET_ALL}\n{full_row}\n{colorama.Fore.YELLOW}{arrows}\n{colorama.Style.RESET_ALL}{reason}\n")
        exit()

    def next(self, *match: str):
        self.pos += 1
        if self.pos >= len(self.source):
            self.tok = Token('EOF', None, len(self.source))
        else:
            self.tok = self.source[self.pos]
        if match != () and self.tok.type == match:
            if self.top.type == match:
                self.error("Expected token: " + match)
            elif self.tok.type in match:
                self.error("Expected one of following tokens token: ['" + ', '.join(match) + "']")

    def empty(self):
        return NoOp()

    def factor(self):
        token = self.tok
        if token.type in ("PLUS", "MINUS"):
            self.next()
            node = UnaryOp(token, self.base())
            return node
        elif token.type == "NUMBER":
            self.next()
            return Num(token)
        elif token.type == "LBRACKET":
            self.next()
            node = self.expr()
            self.next()
            return node
        else:
            node = self.variable()
            return self

    def base(self):
        node = self.factor()

        while self.tok.type == "EXP":
            token = self.tok
            self.next()

            node = BinOp(node, token, self.factor())
        
        return node

    def term(self):
        node = self.base()

        while self.tok.type in ("MUL", "DIV"):
            token = self.tok
            self.next()

            node = BinOp(node, token, self.base())
        
        return node
    
    def expr(self):
        node = self.term()

        while self.tok.type in ("PLUS", "MINUS"):
            token = self.tok
            self.next()

            node = BinOp(node, token, self.term())
        
        return node
    
    def variable(self):
        node = Var(self.tok)
        self.next("ID")
        return node

    def reassignment_statement(self):
        left = self.variable()
        token = self.tok
        if self.tok.type == "EQUALS":
            right = self.expr()
            node = Reassign(left, token, right)
        elif self.tok.type in ("PLUS", "MINUS", "MUL", "DIV", "MOD", "EXP", "DIVDIV"):
            self.next("EQUALS")
            self.next()
            right = self.expr()
            node = Reassign(left, token, right)
        else:
            self.error("Invalid assignment")
        return node

    def assignment_statement(self):
        self.next("ID")
        left = self.variable()
        token = self.tok
        self.next()
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def statement(self):
        if self.tok.type == "LCURLY":
            node = self.scope()
        elif self.tok.type == "LET":
            node = self.assignment_statement()
        elif self.tok.type == "ID":
            node = self.reassignment_statement()
        else:
            node = self.empty()
        return node

    def statement_list(self):
        node = self.statement()

        results = [node]

        while self.tok.type == "SEMI":
            self.next("SEMI")
            results.append(self.statement())

        if self.tok.type == "ID":
            self.error("Expected ;")
        
        return results

    def scope(self):
        self.next("LCURLY")
        nodes = self.statement_list()
        self.next("RCURLY")

        root = Scope()
        for node in nodes:
            root.statements.append(node)

        return root

    def program(self):
        node = self.scope()
        self.next()
        return node

    def parse(self, filename: str | tuple | list = ''):
        self.source = self.tokenizer.tokenize(filename)
        
        self.filename = filename

        self.pos = -1
        self.next()

        node = self.program()
        if self.tok.type != "EOF":
            self.error("Expected end of file")
        return node
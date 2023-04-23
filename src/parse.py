from src.lexer import Token, Tokenizer, colorama, underline_char

##########################################
##                                      ##
##  Parser                              ##
##                                      ##
##########################################

class AST:
    ...

class Scope(AST):
    def __init__(self, statements: list = None) -> None:
        if statements == None: statements = []
        self.statements = statements
    
    def __repr__(self) -> str:
        statements = []
        # print("len: " + repr(len(self.statements)))
        for s in self.statements:
            # print("> " + repr(s))
            statements.append(repr(s))
        return f"Scope({', '.join(statements)})"

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
    
    def __repr__(self) -> str:
        return f"Reassign({self.left}, {self.op}, {self.right})"

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
    def __init__(self, oindex) -> None:
        value = Token("NIL", None, oindex)
    
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
            self.error("Expected <EOF>")
        else:
            self.tok = self.source[self.pos]

        if match != ():
            if len(match) == 1 and self.tok.type != match[0]:
                self.error("Expected token: " + match[0])
            elif len(match) > 1 and self.tok.type not in match:
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
            return node

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
        self.next()
        return node

    def reassignment_statement(self):
        left = self.variable()
        token = self.tok
        if token.type == "EQUALS":
            self.next()
            right = self.expr()
            node = Reassign(left, token, right)
        elif token.type in ("PLUS", "MINUS", "MUL", "DIV", "MOD", "EXP", "DIVDIV"):
            self.next("EQUALS")
            self.next()
            right = self.expr()
            node = Reassign(left, token, right)
        else:
            self.error("Invalid token")
        return node

    def assignment_statement(self):
        self.next("ID")
        left = self.variable()
        token = self.tok
        self.next()
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def print_statement(self):
        self.next()
        node = self.statement()
        return Print(node)

    def return_statement(self):
        self.next()
        node = self.expr()
        return Return(node)

    def statement(self):
        if self.tok.type == "LCURLY":
            node = self.scope()
        elif self.tok.type == "LET":
            node = self.assignment_statement()
        elif self.tok.type == "ID":
            node = self.reassignment_statement()
        elif self.tok.type == "RETURN":
            node = self.return_statement()
        elif self.tok.type == "PRINT":
            node = self.print_statement()
        elif self.tok.type == "RCURLY":
            node = self.empty(self.tok.oindex + 1)
        else:
            node = self.expr()
        return node

    def statement_list(self):
        node = self.statement()

        results = [node]

        while self.tok.type == "SEMI":
            self.next()
            if self.tok.type == "RCURLY":
                break
            results.append(self.statement())

        if self.tok.type == "ID":
            self.error("Expected ;")
        
        return results

    def scope(self):
        if self.tok.type == "LCURLY":
            self.next()
            nodes = self.statement_list()
            if self.tok.type == "RCURLY":
                root = Scope()

                for node in nodes:
                    root.statements.append(node)

                self.next()
                return root
            else:
                self.error("Expected }")
        else:
            self.error("Expected {")

    def program(self):
        node = self.scope()
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
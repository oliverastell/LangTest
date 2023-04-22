from src.lexer import Token, Tokenizer, colorama, underline_char

##########################################
##                                      ##
##  Parser                              ##
##                                      ##
##########################################

class AST:
    ...

class UnaryOp(AST):
    def __init__(self, op, expr) -> None:
        self.token = self.op = op
        self.expr = expr
        self.type = "UnaryOp"
    
    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.expr})"

class BinOp(AST):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.right = right
        self.op = op
        self.type = "BinOp"
    
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

        arrows = ' '*(len(read_row) - len(str(self.tok.value))) + '^' * len(str(self.tok.value))

        print(f"\n{colorama.Fore.RED}{underline_char}AN ERROR OCCURED{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{filename}>: Line {line}{colorama.Style.RESET_ALL}\n{full_row}\n{colorama.Fore.YELLOW}{arrows}\n{colorama.Style.RESET_ALL}{reason}\n")
        exit()

    def next(self):
        self.pos += 1
        if self.pos >= len(self.source):
            self.tok = Token('EOF', None, len(self.source))
        else:
            self.tok = self.source[self.pos] 

    def factor(self):
        token = self.tok
        if token.type in ("PLUS", "MINUS"):
            self.next()
            node = UnaryOp(token, self.base())
            return node
        elif token.type == "NUMBER":
            self.next()
            return token
        elif token.type == "LBRACKET":
            self.next()
            node = self.expr()
            self.next()
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

    def parse(self, filename: str | tuple | list = ''):
        self.source = self.tokenizer.tokenize(filename)
        
        self.filename = filename

        self.pos = -1
        self.next()

        # while self.tok != None:
        #     self.next()
        return self.expr()
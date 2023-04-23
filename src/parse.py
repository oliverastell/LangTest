from src.lexer import Token, Tokenizer, colorama, underline_char
from src.parse_tokens import *

##########################################
##                                      ##
##  Parser                              ##
##                                      ##
##########################################

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

        print(f"\n{colorama.Fore.RED}{underline_char}Parsing Error{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{filename}>: Line {line}{colorama.Style.RESET_ALL}\n{full_row}\n{colorama.Fore.YELLOW}{arrows}\n{colorama.Style.RESET_ALL}{reason}\n")
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

    def empty(self, oindex: int = 0):
        return Nil(oindex)

    def factor(self):
        token = self.tok
        if token.type in ("PLUS", "MINUS"):
            self.next()
            node = UnaryOp(token, self.base())
        elif token.type in ("TRUE", "FALSE"):
            self.next()
            node = Bool(token)
        elif token.type == "NUMBER":
            self.next()
            node = Num(token)
        elif token.type == "STRING":
            self.next()
            node = String(token)
        elif token.type == "LBRACKET":
            self.next()
            node = self.bool_expr()
            self.next()
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

    def bool_relation(self):
        node = self.expr()

        while self.tok.type in ("EQUALSE", "BANGE", "LESSER", "GREATER", "LESSERE", "GREATERE"):
            token = self.tok
            self.next()

            node = BinOp(node, token, self.expr())
        
        return node

    def bool_and(self):
        node = self.bool_relation()

        while self.tok.type == "AND":
            token = self.tok
            self.next()

            node = BinOp(node, token, self.bool_relation())
        
        return node
    
    def bool_expr(self):
        node = self.bool_and()

        while self.tok.type == "OR":
            token = self.tok
            self.next()

            node = BinOp(node, token, self.bool_and())
        
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
            right = self.statement()
            node = Reassign(left, token, right)
        elif token.type in ("PLUS", "MINUS", "MUL", "DIV", "MOD", "EXP", "DIVDIV"):
            self.next("EQUALS")
            self.next()
            right = self.statement()
            node = Reassign(left, token, right)
        else:
            node = left
        return node

    def assignment_statement(self):
        self.next("ID")
        left = self.variable()
        token = self.tok
        self.next()
        right = self.statement()
        node = Assign(left, token, right)
        return node

    def if_statement(self):
        self.next()
        condition = self.bool_expr()
        result = self.scope()
        return If(condition, result)

    def print_statement(self):
        self.next()
        node = self.statement()
        return Print(node)

    def return_statement(self):
        self.next()
        node = self.statement()
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
        # elif self.tok.type == "FN":
        #     node = self.function_definition()
        elif self.tok.type == "IF":
            node = self.if_statement()
        else:
            node = self.bool_expr()
        return node

    def statement_list(self):

        node = self.statement()

        results = [node]
        if self.tok.type == "RCURLY":
            results[-1] = Return(results[-1])
        elif self.tok.type == "SEMI":
            while self.tok.type == "SEMI":
                self.next()
                if self.tok.type == "RCURLY":
                    break
                results.append(self.statement())
                if self.tok.type == "RCURLY":
                    results[-1] = Return(results[-1])
                    break

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
    
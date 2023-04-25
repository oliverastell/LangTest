from src.lexer import Token, Tokenizer, colorama, underline_char
from src.parsetokens import *

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

        print(f"\n{colorama.Fore.RED}{underline_char}Parsing Error{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{filename}>: Line {line} (index: {self.tok.oindex}){colorama.Style.RESET_ALL}\n{full_row}\n{colorama.Fore.YELLOW}{arrows}\n{colorama.Style.RESET_ALL}{reason}\n")
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

    def call(self, node):
        if self.tok.type == "LBRACKET":
            parameters = self.make_tuple()
            node = Call(node, parameters)
        return node

    def factor(self):
        token = self.tok
        print("token:", token)
        if token.type in ("PLUS", "MINUS"):
            self.next()
            node = UnaryOp(token, self.base())
        elif token.type in ("TRUE", "FALSE"):
            self.next()
            node = Bool(token)
        elif token.type == "ID":
            node = self.variable()
        elif token.type == "FUNCTION":
            node = self.func_statement(False, True)
        elif token.type == "NIL":
            self.next()
            node = Nil(token.oindex)
        elif token.type == "NUMBER":
            self.next()
            node = Num(token)
        elif token.type == "STRING":
            self.next()
            node = String(token)
        elif token.type == "LBRACKET":
            self.next()
            if self.tok.type == "RBRACKET":
                return Nil(self.tok.oindex)
            else:
                node = self.bool_expr()
                if self.tok.type != "RBRACKET":
                    self.error("Unclosed Bracket")
                self.next()
        elif token.type == "LCURLY":
            node = self.scope()
        else:
            node = self.variable()

        return self.call(node)

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

    def bool_not(self):
        if self.tok.type == "NOT":
            node = UnaryOp(self.tok, None)
            original = node
            self.next()
            while self.tok.type == "NOT":
                node = UnaryOp(self.tok, node)
                self.next()
            original.expr = self.bool_relation()
        else:
            node = self.bool_relation()
        
        return node

    def bool_and(self):
        node = self.bool_not()

        while self.tok.type == "AND":
            token = self.tok
            self.next()

            node = BinOp(node, token, self.bool_not())
        
        return node
    
    def bool_expr(self):
        node = self.bool_and()

        while self.tok.type == "OR":
            token = self.tok
            self.next()

            node = BinOp(node, token, self.bool_and())
        
        return node
    
    def make_tuple(self, identifiers: bool = False):

        if self.tok.type == "LBRACKET":
            self.next()
            nodes = self.value_list(identifiers)
            if self.tok.type == "RBRACKET":
                if not identifiers:
                    root = Tuple()
                    for node in nodes:
                        root.values.append(node)
                else:
                    root = Parameters()
                    for node in nodes:
                        root.identifiers.append(node)

                self.next()
                return root
            else:
                self.error("Expected )")
        else:
            self.error("Expected (")
    
    def variable(self):
        token = self.tok
        self.next()
        return Var(token)

    def reassignment_statement(self):
        left = self.bool_expr()
        token = self.tok
        if token.type == "EQUALS":
            if type(left) != Var:
                self.error("Cannot asign to non-variable type")
            self.next()
            right = self.bool_expr()
            node = Reassign(left, token, right)
            return
        elif token.type in ("PLUS", "MINUS", "MUL", "DIV", "MOD", "EXP", "DIVDIV"):
            self.next("EQUALS")
            self.next()
            right = self.statement()
            node = Reassign(left, token, right)
        else:
            node = left
        return node

    def assignment_statement(self, public = False):
        self.next("ID")
        left = self.variable()
        self.next()
        right = self.bool_expr()
        node = Assign(left, right, public)
        return node
    
    def func_statement(self, public = False, statement = True):
        self.next("ID", "LBRACKET")
        if self.tok.type == "ID":
            if statement:
                left = self.tok
                self.next("LBRACKET")
                parameters = self.make_tuple(True)
                right = self.scope()
                node = Assign(left, Function(parameters, right), public)
                return node
            else:
                self.error("Cannot define function here")
        elif self.tok.type == "LBRACKET":
            if public:
                self.error("Cannot make an anonymous function public")
            else:
                parameters = self.make_tuple(True)
                right = self.scope()
                node = Function(parameters, right)
                return node
        
    def public_statement(self):
        self.next('FUNCTION', 'LET')
        if self.tok.type == "FUNCTION":
            return self.func_statement(True)
        elif self.tok.type == "LET":
            return self.assignment_statement(True)

    def if_statement(self):
        self.next()
        condition = self.bool_expr()
        result = self.scope(True)
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
        if self.tok.type == "BANG":
            self.next()
            node = self.bool_expr()
        elif self.tok.type == "LCURLY":
            node = self.scope()
        elif self.tok.type == "LET":
            node = self.assignment_statement()
        elif self.tok.type == "FUNCTION":
            node = self.func_statement(False, True)
        elif self.tok.type == "PUB":
            node = self.public_statement()
        elif self.tok.type == "ID":
            node = self.reassignment_statement()
        elif self.tok.type == "RETURN":
            node = self.return_statement()
        elif self.tok.type == "PRINT":
            node = self.print_statement()
        elif self.tok.type == "RCURLY":
            node = self.empty(self.tok.oindex + 1)
        elif self.tok.type == "IF":
            node = self.if_statement()
        else:
            node = self.bool_expr()
        return node

    def value_list(self, identifiers = False):

        if self.tok.type in ("SEMI", "RBRACKET", "RCURLY"):
            return []
        elif identifiers:
            if self.tok.type == "ID":
                node = self.tok
                self.next()
            else:
                self.error("Expected Identifier")
        else:
            node = self.bool_expr()

        results = [node]

        while self.tok.type == "COMMA":
            self.next()
            if self.tok.type in ("SEMI", "RBRACKET", "RCURLY"):
                break

            if identifiers:
                if self.tok.type == "ID":
                    node = self.tok
                    self.next()
                else:
                    self.error("Expected Identifier")
            else:
                node = self.bool_expr()

            results.append(node)
            if self.tok.type in ("SEMI", "RBRACKET", "RCURLY"):
                break

        return results

    def statement_list(self):
        if self.tok.type == "RCURLY":
            return []

        results = [self.statement()]

        if self.tok.type == "RCURLY":
            results[-1] = Return(results[-1])
        elif self.tok.type == "SEMI":
            while self.tok.type == "SEMI":
                self.next()
                if self.tok.type == "RCURLY":
                    break

                node = self.statement()
                results.append(node)
                if self.tok.type == "RCURLY":
                    results[-1] = Return(results[-1])
                    break

        return results

    def scope(self, shares: bool = False):
        parent = None
        if len(self.scope_stack) != 0:
            parent = self.scope_stack[-1]

        if self.tok.type == "LCURLY":
            self.next()
            root = Scope(parent, shares)
            self.scope_stack.append(root)

            nodes = self.statement_list()
            if self.tok.type == "RCURLY":

                for node in nodes:
                    root.statements.append(node)

                self.scope_stack.pop()

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

        self.scope_stack = []

        node = self.program()
        if self.tok.type != "EOF":
            self.error("Expected end of file")
        return node
    
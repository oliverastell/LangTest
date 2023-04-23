import colorama, fileinput

##########################################
##                                      ##
##  Lexer                               ##
##                                      ##
##########################################

NUMBER = '0123456789.'
IDENTIFIER = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_' + NUMBER
WHITESPACE = ' \n\t\r'
STRING_CAP = '"\''
ESCAPE_SEQUENCE = '\\'
OPS = {
    '+': "PLUS",
    '-': "MINUS",
    '*': "MUL",
    '/': "DIV",
    '^': "EXP",
    '%': "MOD",
    '=': "EQUALS",
    '<': "LESSER",
    '>': "GREATER",
    ';': "SEMI",
    '(': "LBRACKET",
    ')': "RBRACKET",
    '{': "LCURLY",
    '}': "RCURLY",
}
EQ_OPS = '=<>'
DO_OPS = '/'
RESERVED = {
    "true": "TRUE",
    "false": "FALSE",
    "print": "PRINT",
    "let": "LET",
}

underline_char = '\033[1;4m'

def repr_float(x):
    if type(x) == float:
        if x.is_integer(): return str(int(x))
        else: return str(float(x))
    else:
        return x

class Token:
    def __init__(self, type: str, value, oindex) -> None:
        self.type = type
        self.value = value
        self.oindex = oindex
    
    def __repr__(self) -> str:
        no_newlines = str(self.value).replace('\n', colorama.Fore.YELLOW + '\\n' + colorama.Style.RESET_ALL)
        if type(self.value) == str:
            no_newlines = '"' + no_newlines + '"'
        return f"Token({self.type}, {no_newlines})"

class Tokenizer:
    def __init__(self, source: str) -> None:
        self.source = '{' + source + '}'
    
    def error(self, reason: str = "Failed to tokenize", length: int = 1):
        read = '\n' + self.source[:self.pos + 1]
        
        read_row = read[read.rfind('\n'):][1:]
        line = read.count('\n')
        full_row = self.source.split('\n')[line - 1]

        if type(self.filename) in (list, tuple):
            filename = self.filename[-1]
        elif type(self.filename) == str:
            filename = self.filename

        arrows = ' '*(len(read_row) - length) + '^' * length

        print(f"\n{colorama.Fore.RED}{underline_char}AN ERROR OCCURED{colorama.Style.RESET_ALL}\n {colorama.Fore.CYAN}<{filename}>: Line {line}{colorama.Style.RESET_ALL}\n{full_row}\n{colorama.Fore.YELLOW}{arrows}\n{colorama.Style.RESET_ALL}{reason}\n")
        exit()

    def next(self) -> None:
        self.pos += 1
        if self.pos >= len(self.source):
            self.char = None
        else:
            self.char = self.source[self.pos]
    
    def make_number(self):
        token = ''
        oindex = self.pos
        periods = 0

        while self.char != None and self.char in NUMBER:
            if self.char == '_':
                continue
            token += self.char

            if self.char == '.':
                periods += 1
                if periods > 1:
                    self.error("Invalid number type")

            self.next()
        return Token('NUMBER', float(token), oindex)

    def make_identifier(self):
        token = ''
        oindex = self.pos

        while self.char != None and self.char in IDENTIFIER:
            token += self.char
            self.next()
        
        if token in RESERVED:
            return Token(RESERVED[token], token, oindex)
        return Token('ID', token, oindex)

    def make_op(self):
        token = self.char
        oindex = self.pos
        self.next()
        if self.char == '=' and token in EQ_OPS:
            self.next()
            return Token(OPS[token] + 'E', token + '=', oindex)
        elif self.char == token and token in DO_OPS:
            self.next()
            return Token(OPS[token]*2, token + token, oindex)
        return Token(OPS[token], token, oindex)
    
    def make_string(self):
        cap = self.char
        token = ''
        oindex = self.pos
        self.next()
        while self.char != None and self.char != cap:
            if self.char == ESCAPE_SEQUENCE:
                self.next()
                if self.char == "n":
                    token += '\n'
                elif self.char == '\\':
                    token += '\\'
                elif self.char in '0123456789_':
                    num = ''
                    while self.char in '0123456789_':
                        num += self.char
                        self.next()
                    token += chr(int(num))
                    if self.char != '\\':
                        token += self.char
            else:
                token += self.char
            self.next()
        self.next()
        return Token('STRING', token, oindex)

            
    def tokenize(self, filename: str | list | tuple = ''):
        self.pos = -1
        self.next()
        self.filename = filename

        tokens = []

        while self.char != None:
            if self.char in NUMBER:
                tokens.append(self.make_number())
            elif self.char in IDENTIFIER:
                tokens.append(self.make_identifier())
            elif self.char in OPS:
                tokens.append(self.make_op())
            elif self.char in STRING_CAP:
                tokens.append(self.make_string())
            elif self.char in WHITESPACE:
                self.next()
            else:
                self.error(f"Invalid Character: '{self.char}'")
        
        return tokens

if __name__ == "__main__":
    print('\n' + str(Tokenizer(fileinput.file_input()).tokenize('stdin')))
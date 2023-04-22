import src.libs.longinput as longinput
from src.lexer import Tokenizer
from src.parse import Parser
from src.interpreter import Interpreter

if __name__ == "__main__":
    while True:
        tokenizer = Tokenizer(longinput.file_input())
        parser = Parser(tokenizer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret('stdin')

        print(str(result))
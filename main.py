import time, sys
import src.libs.longinput as longinput
from src.lexer import Tokenizer
from src.parse import Parser
from src.interpreter import Interpreter

sys.setrecursionlimit(50)

if __name__ == "__main__":
    while True:
        tokenizer = Tokenizer(longinput.file_input())
        parser = Parser(tokenizer)

        # print(parser.parse())
        interpreter = Interpreter(parser)
        result = interpreter.interpret('stdin')

        print(interpreter.GLOBAL_SCOPE)
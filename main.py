import src.libs.longinput as longinput
from src.lexer import Tokenizer
from src.parse import Parser
from src.interpreter import Interpreter

file = "test.tl"
# file = "stdin"

if __name__ == "__main__":
    if file == "stdin":
        while True:
            tokenizer = Tokenizer(longinput.long_input())
            parser = Parser(tokenizer)

            interpreter = Interpreter(parser)
            result = interpreter.interpret('stdin')

            print(interpreter.GLOBAL_SCOPE)
    else:
        tokenizer = Tokenizer(longinput.file_input(file))
        parser = Parser(tokenizer)

        interpreter = Interpreter(parser)
        result = interpreter.interpret(file)

        print(interpreter.GLOBAL_SCOPE)

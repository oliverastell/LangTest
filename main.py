import src.libs.longinput as longinput
from src.lexer import Tokenizer
from src.parse import Parser
from src.interpreter import Interpreter

file = "test.lt"
# file = "stdin"

def main():
    repeat = True
    while repeat:
        if file != "stdin": 
            repeat = False
            tokenizer = Tokenizer(longinput.file_input(file))
        else:
            tokenizer = Tokenizer(longinput.long_input())
        parser = Parser(tokenizer)

        tree = parser.parse()

        interpreter = Interpreter(tree)
        interpreter.interpret('stdin')

        print("\nGLOBAL_MEMORY:")
        for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
            print(f"{k} = {v}")

if __name__ == "__main__":
    main()
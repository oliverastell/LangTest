import colorama
import src.libs.longinput as longinput
from src.lexer import Tokenizer
from src.parse import Parser
from src.interpreter import Interpreter
import sys

sys.setrecursionlimit(50)

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

        # print(tree)

        print('')
        interpreter = Interpreter(tree)
        interpreter.interpret('stdin')

        print(f"\n{colorama.Fore.YELLOW}GLOBAL MEMORY:")
        for k, v in sorted(interpreter.global_scope.vars.items()):
            print(f"{colorama.Fore.CYAN}{k}{colorama.Fore.WHITE} = {v}")
        print()

if __name__ == "__main__":
    main()
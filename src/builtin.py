from src.parsetokens import *
import src.parsetokens, importlib
from types import FunctionType, NoneType

def get_globals():

    def expect_amount(length, parameters):
        if len(parameters) >= length:
            return True
        else:
            return False
    def lack_parameters():
        return py_eval(Exception("Not enough parameters entered"))
    
    def py_eval(object = None):
        if type(object) == Exception:
            return Error(py_eval(' '.join(object.args)))
        elif type(object) == str:
            return String(Token("STRING", object, 0))
        elif type(object) in (int, float):
            return Num(Token("NUMBER", float(object), 0))
        elif type(object) == NoneType:
            return Nil(0)
        elif type(object) == FunctionType:
            return Function(object)
        return py_eval(Exception(f"Cannot evaluate type: <{type(object).__name__}>"))

    def print_func(*parameters):
        if not expect_amount(0, parameters):
            return lack_parameters()

        value = ''
        for x in parameters:
            value += " " + x.string()

        value = value[1:]

        print(value)

        return py_eval()
    
    def python(*parameters):
        if not expect_amount(1, parameters):
            return lack_parameters()
        value = None
        try:
            py_globals = {}
            exec(parameters[0].token.value, py_globals)
            value = py_globals['main']()
        except Exception as ex:
            value = Exception(' '.join(ex.args))
        return py_eval(value)

    return {
    "print": Function(print_func),
    "python": Function(python),
    }

src.parsetokens.default_vars = get_globals()
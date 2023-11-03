from enum import Enum

TOKEN_TYPES = {
    'KEYWORD', # reserved words such as if, else, while, etc.
    'IDENTIFIER', # variable names, function names, etc.
    'SEPARATOR', # punctuation such as (, ), {, }, etc.
    'OPERATOR', # operators such as +, -, *, /, etc.
    'LITERAL', # numeric literals such as 1, 2, 3, etc.
}

OPERATORS = ["+", "-", "*", "/", "%", "=","<", ">", "!"]

class TokenType(Enum):
        KEYWORD = 0 # reserved words such as if, else, while, etc.
        IDENTIFIER = 1  # variable names, function names, etc.
        SEPARATOR = 2 # punctuation such as (, ), {, }, etc.
        OPERATOR = 3 # operators such as +, -, *, /, etc.
        LITERAL = 4 # numeric literals such as 1, 2, 3, etc.

class Token:
    def __init__(self, type: TokenType, value: str, line_number: int, column_number: int) -> None:
        self.type = type
        self.value = value
        self.line_number = line_number
        self.column_number = column_number

    def __repr__(self) -> str:
         class_name = self.__class__.__name__
         return f'{class_name}({self.type}, {self.value}, {self.line_number}, {self.column_number})'
    
    def __str__(self) -> str:
         return f'{self.type}, {self.value}'

class TokenizerState(Enum):
    NEXT_TOKEN = 0
    IN_TOKEN = 1
    IN_OPERATOR_TOKEN = 2


def toknize(source_code):
    """
    sample function, gets source code and returns a list of tokens
    if fails, raises an exception
    """
    tokens = []
    
    #tokens.append(Token(TokenType.IDENTIFIER, 'sum', 1, 4))
    #tokens.append(Token(TokenType.KEYWORD, 'if', 1, 0))
    #now we will iterate over the source code and extract tokens, and iterare line by line and char by char
    line_number = 1
    column_number = 1
    state = TokenizerState.NEXT_TOKEN
    stack = []

    #iterate over the source code line by line
    for char in source_code:
        if state == TokenizerState.NEXT_TOKEN:
            if char.isspace():
                #if it is, ignore it
                pass
            if char.isalphanum() or char == '_':
                stack.append(char)
                state = TokenizerState.IN_TOKEN
                pass
            if char == "+":
                stack.append(char)
                state = TokenizerState.IN_OPERATOR_TOKEN
                pass
        elif state == TokenizerState.IN_TOKEN:
            pass
        else:
            raise Exception(f'Unknown state: {state}')
    
    

    if __name__ == '__main__':
        with open("sum.c", "r") as f:
            source_code = f.read()
        #get source code from file or stdin
        # check if there is a file name in the command line arguments
        #import sys
        #if False and len(sys.argv) > 1:
        #    
        #    with open(sys.argv[1]) as f:
        #        source_code = f.read()
        #else: 
        #    source_code = sys.stdin.read()
        #
        tokens = toknize(source_code)

        print(repr(tokens))
        
        pass
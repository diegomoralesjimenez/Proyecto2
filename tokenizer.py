# enum for token types

from enum import Enum


OPERATORS = [
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    "<",
    ">",
    "!",
    "&",
    "|",
    "^",
    "~",
    "?",
    ":",
    ";",
    ",",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    ",",
]

TYPES = ["string", "int", "float", "void", "bool"]

KEYWORDS = [
    "if",
    "else",
    "while",
    "for",
    "return",
    "break",
    "continue",
    "true",
    "false",
]


class TokenType(Enum):
    KEYWORD = 0  # reserved words such as if, else, while, etc.
    IDENTIFIER = 1  # variable names, function names, etc.
    OPERATOR = 2  # operators such as +, -, *, /, etc.
    LITERAL = 3  # numeric literals or string literals such as 123, 3.14, "hello", etc.
    TYPE = 4  # types such as int, float, string, etc.


class Token:
    def __init__(
        self, type: TokenType, value: str, line_number: int, char_number: int
    ) -> None:
        self.type = type
        self.value = value
        self.line_number = line_number
        self.char_number = char_number

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.type}, '{self.value}', {self.line_number}, {self.char_number})"

    def __str__(self) -> str:
        return f"'{self.value}'"

    @staticmethod
    def create_token(
        type: TokenType, value: str, line_number: int, char_number: int
    ) -> None:
        return Token(type, value, line_number, char_number - len(value))


class TokenizerState(Enum):
    NEXT_TOKEN = 0
    IN_TOKEN = 1
    IN_OPERATOR_TOKEN = 2
    IN_STRING_LITERAL = 3
    IN_DIGIT_LITERAL = 4


# tokenizer exception
class TokenizerException(Exception):
    def __init__(
        self, message: str, line_number: int, char_number: int, file_name: str
    ) -> None:
        self.message = message
        self.line_number = line_number
        self.char_number = char_number
        self.file_name = file_name

    def __str__(self) -> str:
        return f"TKN: {self.message} - {self.file_name}:{self.line_number},{self.char_number}"


def tokenize(file_name, source_code):
    tokens = []
    # state variables
    line_number = 1
    char_number = 0
    state = TokenizerState.NEXT_TOKEN
    stack = []

    # iterate over the source code
    for char in source_code:
        char_number += 1
        # switch depending on the state
        if state == TokenizerState.NEXT_TOKEN:
            if char == '"' or char == "'":
                # if it is, start a string literal
                stack.append(char)
                state = TokenizerState.IN_STRING_LITERAL
            # check if the char is a space character
            elif char.isspace():
                # if it is, ignore it
                if char == "\n":
                    line_number += 1
                    char_number = 0
            # check if is a letter
            elif char.isalpha() or char == "_":
                # if it is, start an identifier
                stack.append(char)
                state = TokenizerState.IN_TOKEN
            elif char in OPERATORS:
                # if it is, start an operator
                stack.append(char)
                state = TokenizerState.IN_OPERATOR_TOKEN
            elif char.isdigit() or char == "+" or char == "-":
                # if it is, start a literal
                stack.append(char)
                state = TokenizerState.IN_DIGIT_LITERAL
            else:
                # not expected character
                raise TokenizerException("Unexpected character", line_number, char_number, file_name)
        elif state == TokenizerState.IN_TOKEN:
            # check if continues with the identifier
            if char.isalnum() or char == "_":
                # if it is, add it to the identifier
                stack.append(char)
            elif char.isspace():
                # if it is, add the identifier to the tokens
                token_type = TokenType.IDENTIFIER
                if "".join(stack) in KEYWORDS:
                    token_type = TokenType.KEYWORD
                elif "".join(stack) in TYPES:
                    token_type = TokenType.TYPE
                tokens.append(
                    Token.create_token(
                        token_type, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                state = TokenizerState.NEXT_TOKEN
                if char == "\n":
                    line_number += 1
                    char_number = 0
            elif char in OPERATORS:
                # if it is, add the identifier to the tokens
                token_type = TokenType.IDENTIFIER
                if "".join(stack) in KEYWORDS:
                    token_type = TokenType.KEYWORD
                elif "".join(stack) in TYPES:
                    token_type = TokenType.TYPE
                tokens.append(
                    Token.create_token(
                        token_type, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_OPERATOR_TOKEN
            else:
                # not expected character
                raise TokenizerException("Unexpected character", line_number, char_number, file_name)
        elif state == TokenizerState.IN_OPERATOR_TOKEN:
            if char.isspace():
                # add the operator to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.OPERATOR, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                state = TokenizerState.NEXT_TOKEN
                if char == "\n":
                    line_number += 1
                    char_number = 0
            elif char in OPERATORS:
                if char in OPERATORS:
                    current_operator = "".join(stack)
                    # check the operator to see if is a multi-character operator
                    if (
                        # operators followed by an equal sign
                        (
                            current_operator
                            in ("!", "+", "-", "*", "/", "%", "<", ">", "&", "|", "^")
                            and char == "="
                        )
                        or
                        # operators followed by the same operator
                        (
                            current_operator in ("&", "|", "+", "-", "<", ">", "=", "!")
                            and char == current_operator
                        )
                    ):
                        stack.append(char)
                        tokens.append(
                            Token.create_token(
                                TokenType.OPERATOR,
                                "".join(stack),
                                line_number,
                                char_number,
                            )
                        )
                        stack = []
                        state = TokenizerState.NEXT_TOKEN

                    else:
                        # not a continuaton of the current operator,
                        # so we add the current operator to the tokens
                        tokens.append(
                            Token.create_token(
                                TokenType.OPERATOR,
                                "".join(stack),
                                line_number,
                                char_number,
                            )
                        )
                        stack = []
                        stack.append(char)
                        state = TokenizerState.IN_OPERATOR_TOKEN
                elif char.isalnum() or char == "_":
                    # not a continuation of the current operator,
                    # so we add the current operator to the tokens
                    tokens.append(
                        Token.create_token(
                            TokenType.OPERATOR,
                            "".join(stack),
                            line_number,
                            char_number,
                        )
                    )
                    stack = []
                    stack.append(char)
                    state = TokenizerState.IN_TOKEN
                else:
                    # not expected character
                    raise TokenizerException("Caracter inesperado", line_number, char_number, file_name)
            # check if we are in a string literal
            elif char == '"' or char == "'":
                # if it is, add the operator to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.OPERATOR, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_STRING_LITERAL
            else:
                # the same case as space, but we need to add the operator to the tokens
                # and change the state to IN_TOKEN
                tokens.append(
                    Token.create_token(
                        TokenType.OPERATOR, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_TOKEN
        elif state == TokenizerState.IN_STRING_LITERAL:
            # check if is a new line
            if char == "\n":
                # if it is, raise an exception
                raise TokenizerException("Nueva linea inesperada", line_number, char_number, file_name)
            elif char == stack[0]:
                # check if a backslash is before the quote
                if stack[-1] == "\\":
                    # if it is, add the quote to the string literal
                    stack.append(char)
                else:
                    # if it is not, add the string literal to the tokens
                    stack.append(char)
                    tokens.append(
                        Token.create_token(
                            TokenType.LITERAL, "".join(stack), line_number, char_number
                        )
                    )
                    stack = []
                    state = TokenizerState.NEXT_TOKEN
            else:
                # if it is not, add the char to the string literal
                stack.append(char)
        elif state == TokenizerState.IN_DIGIT_LITERAL:
            if char.isdigit():
                # if it is, add the digit to the literal
                stack.append(char)
            elif char == ".":
                # we need to check the stack to see if there is a dot
                if "." in stack:
                    # if it is, raise an exception
                    raise TokenizerException("Unexpected decimal point", line_number, char_number, file_name)
                else:
                    # if it is not, add the dot to the literal
                    stack.append(char)
            elif char in OPERATORS:
                # if it is, add the literal to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.LITERAL, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_OPERATOR_TOKEN
            elif char == '"' or char == "'":
                # if it is, add the literal to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.LITERAL, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_STRING_LITERAL
            elif char.isspace():
                # if it is, add the literal to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.LITERAL, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                state = TokenizerState.NEXT_TOKEN
                if char == "\n":
                    line_number += 1
                    char_number = 0
            elif char.isalpha() or char == "_":
                # if it is, add the literal to the tokens
                tokens.append(
                    Token.create_token(
                        TokenType.LITERAL, "".join(stack), line_number, char_number
                    )
                )
                stack = []
                stack.append(char)
                state = TokenizerState.IN_TOKEN
            else:
                raise TokenizerException("Unexpected character", line_number, char_number, file_name)
        else:
            raise TokenizerException("Unknown state", line_number, char_number, file_name)
    if len(stack) != 0:
        if state == TokenizerState.IN_OPERATOR_TOKEN:
            state = TokenizerState.NEXT_TOKEN
        elif (
            state == TokenizerState.IN_STRING_LITERAL
            or state == TokenizerState.IN_DIGIT_LITERAL
        ):
            # save the existing literal in the state it is
            tokens.append(
                Token.create_token(
                    TokenType.LITERAL, "".join(stack), line_number, char_number
                )
            )
        else:
            raise TokenizerException(f"Unexpected end of file, current state: {str(state)}", line_number, char_number, file_name)
    return tokens


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # read source code from file
        with open(sys.argv[1], "r") as f:
            source_code = f.read()
    else:
        # read source code from stdin
        print(f"usage: python {sys.argv[0]} <path_to_source_code_file>")
        quit(1)

    # tokenize source code
    tokens = tokenize(sys.argv[1], source_code)
    print(",".join([str(token) for token in tokens]))
    pass


#Nota. Para probar el tokenizer hay que poner en la terminal: python tokenizer.py test.c, este se carga de dividr el codigo para saber que lo compone
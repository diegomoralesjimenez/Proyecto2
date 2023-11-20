from typing import List
from enum import Enum


from tokenizer import *

GROUPING_SYMBOLS = [
    # parenthesis
    "(",
    ")",
    # curly brackets
    "{",
    "}",
    # square brackets
    "[",
    "]",
]

ASSIGNMENT_OPERATORS = [
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "<<=",
    ">>=",
    "&=",
    "^=",
    "|=",
]

INITIAL_ASSIGN_OPERATOR = [
    "+",
    "-",
    "!",
    "&",
    "~",
    "(",
]


class LexerState(str, Enum):
    NEXT_STATEMENT = "NEXT_STATEMENT"
    IN_DEFINITION = "IN_DEFINITION"
    # used for function parameters
    VAR_LIST = "VAR_LIST"
    # used to wait for a function body
    EXPECTING_BODY_BLOCK = "EXPECTING_BODY_BLOCK"
    IN_IF_CONDITION = "IN_IF_CONDITION"
    IN_FOR_INIT = "IN_FOR_INIT"


class ExpressionKind(str, Enum):
    FUNCTION = "FUNCTION"
    VARIABLE_DECLARATION = "VARIABLE_DECLARATION"
    VARIABLE_INITILIZATION = "VARIABLE_INITILIZATION"
    VARIABLE_ASSIGNMENT = "VARIABLE_ASSIGNMENT"
    LITERAL = "LITERAL"
    BINARY_OPERATOR = "BINARY_OPERATOR"
    IDENTIFIER = "IDENTIFIER"
    IF_STATEMENT = "IF_STATEMENT"
    FOR_STATEMENT = "FOR_STATEMENT"


class Error(Exception):
    def __init__(
        self, message: str, line_number: int, char_number: int, file_name: str
    ) -> None:
        self.message = message
        self.line_number = line_number
        self.char_number = char_number
        self.file_name = file_name

    def __str__(self) -> str:
        return f"- Linea:{self.line_number}: {self.message}"


def lex(
    file_name: str,
    tokens: List[Token],
    state: LexerState = LexerState.NEXT_STATEMENT,
    is_root: bool = True,
    start_token: str = None,
):
    root_node = []

    state = LexerState.NEXT_STATEMENT
    current_statement = None
    stack = []

    # check if tokens is a list or an iterator

    it = enumerate(tokens)

    for steps, token in it:
        if state == LexerState.NEXT_STATEMENT:
            if token.type == TokenType.TYPE:
                state = LexerState.IN_DEFINITION
                current_statement = {
                    "type": token.value,
                }
            elif not is_root:
                if token.type == TokenType.LITERAL:
                    current_statement = {
                        "type": token.value,
                    }
                    root_node.append(current_statement)
                elif start_token in ASSIGNMENT_OPERATORS and token.value == ";":
                    # steps will always be the number of elements that have been consumed
                    return (steps + 1, root_node)
                # other binary operators
                elif token.type == TokenType.OPERATOR:
                    current_statement = {
                        "type": token.value,
                    }
                    root_node.append(current_statement)
                # identifier
                elif token.type == TokenType.IDENTIFIER:
                    current_statement = {
                        "name": token.value,
                        "Kind": ExpressionKind.VARIABLE_ASSIGNMENT,
                    }
                    # the next state expects an assignment operator
                    state = LexerState.IN_DEFINITION
                elif token.value == "if" or token.value == "while":
                    current_statement = {
                        "Kind": ExpressionKind.IF_STATEMENT,
                        "condition": None,
                        "body": None,
                        "else_if_clauses": [],
                        "else_clause": None,
                    }
                    state = LexerState.IN_IF_CONDITION  
                elif token.value == "for":
                    current_statement = {
                        "Kind": ExpressionKind.FOR_STATEMENT,
                        "init": None,
                        "condition": None,
                        "post": None,
                        "body": None,
                    }
                    state = LexerState.IN_FOR_INIT
                else:
                    raise Error(
                        f"{str(token)} no es valido",
                        token.line_number,
                        token.char_number,
                        file_name,
                    )
            else:
                raise Error(
                    f"Expected type got {str(token)}",
                    token.line_number,
                    token.char_number,
                    file_name,
                )
        elif state == LexerState.IN_DEFINITION:
            # we need to check if there is already a name
            if "name" in current_statement:
                if token.type == TokenType.OPERATOR:
                    if token.value == ";":
                        # if the type is none then it just an usage of the variable
                        if not "type" in current_statement:
                            current_statement["Kind"] = ExpressionKind.IDENTIFIER
                            root_node.append(current_statement)
                            return (steps + 1, root_node)

                        current_statement["Kind"] = ExpressionKind.VARIABLE_DECLARATION
                        state = LexerState.NEXT_STATEMENT
                        root_node.append(current_statement)
                    elif token.value in ASSIGNMENT_OPERATORS:
                        # if we do not know the type, we now that it is an assignment
                        # so do not override the kind
                        if not "type" in current_statement:
                            current_statement["Kind"] = ExpressionKind.VARIABLE_INITILIZATION
                        current_statement["assign_type"] = token.value
                        (sub_steps, sub_statement) = lex(
                            file_name,
                            tokens[steps + 1 :],
                            LexerState.NEXT_STATEMENT,
                            False,
                            token.value,
                        )
                        # move steps in case there is no more statements
                        steps += sub_steps
                        # we have to skip n steps for it
                        [next(it) for _ in range(sub_steps)]

                        current_statement["value"] = sub_statement
                        state = LexerState.NEXT_STATEMENT
                        root_node.append(current_statement)
                    elif token.value == "(":
                        current_statement["Kind"] = ExpressionKind.FUNCTION
                        state = LexerState.VAR_LIST
                        current_statement["parameters"] = []
                    elif token.value == ">":
                        # Handle the ">" operator within an if statement
                        current_statement = {
                            "type": token.value,
                            "Kind": ExpressionKind.BINARY_OPERATOR,
                        }
                        root_node.append(current_statement)
                else:
                    raise Error(
                        f"Expected assignment or declaration got {str(token)}",
                        token.line_number,
                        token.char_number,
                        file_name,
                    )
                    
            else:
                if token.type == TokenType.IDENTIFIER:
                    current_statement["name"] = token.value
                elif token.type == TokenType.LITERAL:
                    current_statement["value"] = token.value
                    current_statement["Kind"] = ExpressionKind.LITERAL
                elif token.type == TokenType.OPERATOR and token.value == ")":
                    # Handle the closing parenthesis in a way that makes sense for your language
                    root_node.append(current_statement)  # Add the current statement before transitioning
                    current_statement = {}  # Reset the current statement dictionary
                    state = LexerState.NEXT_STATEMENT

                else:
                    raise Error(
                        f"Expected identifier got {str(token)}",
                        token.line_number,
                        token.char_number,
                        file_name,
                    )
        elif state == LexerState.VAR_LIST:
            # check if there is an element in the stack which is a type
            if len(stack) == 0:
                if token.type == TokenType.TYPE:
                    stack.append(token.value)
                elif token.value == ")":
                    # check that there is no past comma
                    if len(current_statement["parameters"]) > 0:
                        raise Error(
                            f"Error de )",
                            token.line_number,
                            token.char_number,
                            file_name,
                        )

                    state = LexerState.EXPECTING_BODY_BLOCK
                else:
                    raise Error(
                        f"'{token}' no es valido como un tipado",
                        token.line_number,
                        token.char_number,
                        file_name,
                    )
            elif len(stack) == 1:
                if token.type == TokenType.IDENTIFIER:
                    stack.append(token.value)
                else:
                    raise Error(
                        f"Expected identifier got {str(token)}",
                        token.line_number,
                        token.char_number,
                        file_name,
                    )
            # there is already a name and the type, expecting a , or a )
            else:
                if token.value == ",":
                    current_statement["parameters"].append(
                        {"type": stack[0], "name": stack[1]}
                    )
                    stack = []
                elif token.value == ")":
                    current_statement["parameters"].append(
                        {"type": stack[0], "name": stack[1]}
                    )
                    stack = []
                    state = LexerState.EXPECTING_BODY_BLOCK
        elif state == LexerState.EXPECTING_BODY_BLOCK:
            if token.value == "{":
                state = LexerState.NEXT_STATEMENT
                sub_steps, current_statement["body"] = lex(
                    file_name, tokens[steps + 1 :], LexerState.NEXT_STATEMENT, False
                )
                # move steps in case there is no more statements
                steps += sub_steps
                # we have to skip n steps for it
                [next(it) for _ in range(sub_steps)]

                root_node.append(current_statement)
            else:
                raise Error(
                    f"Expected {{ got {str(token)}",
                    token.line_number,
                    token.char_number,
                    file_name,
                )
        elif state == LexerState.IN_IF_CONDITION:
            if token.value == "(":
                state = LexerState.NEXT_STATEMENT
                (sub_steps, condition) = lex(
                    file_name, tokens[steps + 1 :], LexerState.NEXT_STATEMENT, False
                )
                # move steps in case there is no more statements
                steps += sub_steps
                # we have to skip n steps for it
                [next(it) for _ in range(sub_steps)]

                current_statement["condition"] = condition
                state = LexerState.EXPECTING_BODY_BLOCK
            else:
                raise Error(
                    f"Expected ( after if keyword, got {str(token)}",
                    token.line_number,
                    token.char_number,
                    file_name,
                )

    return (steps + 1, root_node)


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
    _, tree = lex(sys.argv[1], tokens)
    # convert the dictionary to a json string
    import json

    # save it to tree.json
    with open("tree.json", "w") as f:
        f.write(json.dumps(tree, indent=4))

    print("El codigo se leyo correctamente")
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
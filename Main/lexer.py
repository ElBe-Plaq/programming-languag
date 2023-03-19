# HEADER


###########
# IMPORTS #
###########

import ast
from typing import (
    Any,
    List
)


#############
# CONSTANTS #
#############

DIGITS: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
DIGITS_AS_STRINGS: List[str] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]


##############
# MAIN LEXER #
##############

class LexerToken:
    def __init__(self, token_type: Any, value: Any) -> None:
        self.type = token_type
        self.value = value

    def __str__(self) -> str:
        return "{" + self.type + ":'" + self.value + "'}"

    def __repr__(self) -> str:
        return "{" + self.type + ":'" + self.value + "'}"


class LexerError(BaseException):
    def __init__(self, description: str, line: int, column: int) -> None:
        self.desc = description
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return str(self.desc) + " in line " + str(self.line) + ", column " + str(self.column)


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.separators = [" ","\t","\n"]
        self.doublemarks = {
            "==": "EQUAL",
            "++": "COUNT_UP",
            "--": "COUNT_DOWN"
        }
        self.marks = {
            ';': "END_CMD",
            "=": "SET",
            "{": "BLOCK_OPEN",   # Also dicts
            "}": "BLOCK_CLOSE",  # Also dicts
            "(": "CLAMP_OPEN",
            ")": "CLAMP_CLOSE",
            "[": "INDEX_OPEN",   # Also arrays
            "]": "INDEX_CLOSE",  # Also arrays
            "?": "INDEFINITE",
            ".": "SEPERATOR",
            ":": "SLICE",
            ">": "GREATER",
            "<": "LESS",
            "+": "ADD",
            "-": "SUBTRACT",
            "*": "MULTIPLY",
            "/": "DIVIDE",
            "%": "STRING_FORMATTER"
        }
        self.keywords = {
            "class": "CLASS",
            "use": "USE",
            "import": "IMPORT",
            "if": "IF",
            "else": "ELSE",
            "while": "WHILE",
            "for": "FOR",
            "return": "RETURN",
            "delete": "DELETE",
            "break": "BREAK",
            "continue": "CONTINUE",
        }
        self.basetypes = [
            "string",  # and str
            "int",     # and integer
            "float",
            "complex",
            "list",     # and array
            "dict",     # and dictionary
            "bool",
            "dynamic",
            "None"      # CONST, can't be changed
        ]
        
        self.tokens = []
        
    def lex(self):
        def validate_float(string: str) -> bool:
            dot = False
            valid = True
            
            if string[0] == "-":
                string = string[1:]
            for char in string:
                valid = valid and (char in DIGITS_AS_STRINGS or (char == "." and not dot))
                if char == ".":
                    dot = True
            return valid

        def validate_integer(string: str) -> bool:
            valid = True
            if string[0] == "-":
                string = string[1:]
            for char in string:
                valid = valid and char in ["0","1","2","3","4","5","6","7","8","9"]
                
            return valid
        
        def gettoken(string: str, l, c) -> LexerToken: # What's l and c, find better names
            if string in list(self.keywords.keys()):
                return LexerToken(self.keywords[string],string)
            elif len(string) > 0 and string[0] == "_":
                return LexerToken("BUILTIN_CONST",string)
            elif string == "true" or string == "false":
                return LexerToken("BOOL", string)
            elif string in self.basetypes:
                return LexerToken("BASETYPE", string)
            elif len(string) == 0:
                return None
            elif validate_float(string):
                if validate_integer(string): return LexerToken("INT" ,string)
                return LexerToken("FLOAT",string)
            
            elif len(string) > 0 and string[0] not in ["0","1","2","3","4","5","6","7","8","9"]:
                return LexerToken("NAME",string)
            
            else:
                raise LexerError("Unrecognized Pattern: '" + string + "'",l,c)

        def repl(ar):
            n = []
            for el in ar:
                if el is not None:
                    n.append(el)
            return n
        line = 1
        comment = 0
        column = 1
        index = 0
        buffer = ""
        instring = False
        while index < len(self.text):
            if self.text[index] == "\n":
                self.tokens.append(gettoken(buffer,line,column))
                line += 1
                column = 1
                buffer = ""
                if comment == 1: comment = 0
            else: column += 1
            if comment < 1:
                
                if (len(self.text[index:])>1 and self.text[index:index+2]=="//"):
                    comment = 1
                elif self.text[index] == "'" or self.text[index] == "\"":
                    instring = not instring
                    if not instring:
                        self.tokens.append(LexerToken("STRING",buffer))
                        
                        buffer = ""
                    
                elif instring:
                    buffer += self.text[index]
                elif self.text[index] in self.separators:
                    self.tokens.append(gettoken(buffer,line,column))
                    buffer = ""
                elif len(self.text[index:])>1 and self.text[index:index+2] in list(self.doublemarks.keys()):
                    self.tokens.append(gettoken(buffer,line,column))
                    self.tokens.append(LexerToken(self.doublemarks[self.text[index:index+2]],self.text[index:index+2]))
                    buffer = ""
                    index += 1
                    
                elif self.text[index] in list(self.marks.keys()):
                    self.tokens.append(gettoken(buffer,line,column))
                    self.tokens.append(LexerToken(self.marks[self.text[index]],self.text[index]))
                    buffer = ""
                
                else:
                    buffer += self.text[index]
            
            index += 1
        self.tokens = repl(self.tokens)
        return self.tokens
        
if __name__ == "__main__":
    f = open("arraysfile.ilang")
    d = f.read()
    f.close()
    l = Lexer(d)
    print(l.lex())

from __future__ import annotations
from typing import Optional, Dict, List
from dataclasses import dataclass, field

import sys

from lat import compiler_warning, compiler_error, compiler_note, std_message

@dataclass
class FunctionData:
    """
    Class That represents everything about a function.
    Input values and output values are missing but should be added later to provide for a better compiler.
    """
    name: str
    input_types: Optional[List[str]] = field(default_factory=list)
    output_type: Optional[str] = None

@dataclass
class Functions:
    """
    Class that holds all the functions.
    """
    Table: Dict[str, FunctionData] = field(default_factory=dict)    # Table of functions
    current_function: Optional[FunctionData] = None                 # Current function

    def __post_init__(self):
        self.productions = {
            "call": self._call,
            "header": self._header,
            "id": self._id,
            "body": self._body,
            "parameter": self._parameter,
            "out_type": self._out_type,
            "argument": self._argument,
            "return": self._return,
        }

    def handle(self, p, production: str):
        return self.productions[production](p)

    def add(self, name: str) -> None:   # Adds a function to the table
        self.Table[name] = FunctionData(name)

    def get(self, name: str) -> Optional[FunctionData]:  # Gets a function from the table if it exists
        return self.Table.get(name)

    def _header(self, p):  # Declares a function
        """
        function_header : function_id ss '(' params ')' out_type
        """
        p.parser.num_params = 0
        return p[1] + p[4]

    def _id(self, p):  # Adds the ID of a function
        """
        function_id : FUNCTION ID
        """
        if p.parser.functions_handler.get(p[2]) is not None:
            compiler_error(p, 2, f"Redefinition of function {p[2]}")
            compiler_note("Called from Functions._id")
            sys.exit(1)
        p.parser.functions_handler.add(p[2])
        p.parser.functions_handler.current_function = p.parser.functions_handler.get(p[2])
        return std_message([f"{p[2].replace('_', '')}:"])

    def _body(self, p):  # Adds the body of a function
        """
        function_body : '{' stmts '}' es
        """
        if not p[2].endswith("RETURN\n"):
            if p.parser.functions_handler.current_function.output_type is not None:
                compiler_warning(p, 3, f"Reached end of function {p.parser.functions_handler.current_function.name} without an explicit return statement.")
                compiler_note("Called from Functions._body")
            else:
                p[2] += "RETURN\n"

        out = p[2]
        p.parser.functions_handler.current_function = None
        return out

    def _parameter(self, p):  # Adds a parameter to the function
        """
        param : ID ':' type
            | ID ':' Ptype
        """
        p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
        p.parser.functions_handler.current_function.input_types.append(p[3])
        p.parser.frame_count += 1
        p.parser.num_params += 1
        return std_message(["PUSHI 0", "PUSHFP", f"LOAD {-p.parser.num_params}", f"STOREL {p.parser.num_params-1}"])

    def _argument(self, p):  # Adds an argument to the function
        """
        arg : expression
        """
        p.parser.num_args[-1] += 1
        return p[1]

    def _out_type(self, p):  # Adds the output type of a function
        """
        out_type : RARROW type
                | 
        """
        if len(p) == 3:
            p.parser.functions_handler.current_function.output_type = p[2]
        return ""

    def _call(self, p):  # Calls a function
        """
        function_call : f_call '(' args ')'
        """
        func = self.get(p[1])
        if func is None:  # If the function doesn't exist, report an error
            compiler_error(p, 1, f"Function {p[1]} not declared")
            compiler_note(f"Error on Function '{p.parser.functions_handler.current_function.name}'")
            compiler_note("Called from Functions._call")
            sys.exit(1)
        if len(func.input_types) != p.parser.num_args[-1]:  # If the number of arguments doesn't match the number of parameters, report an error
            compiler_error(p, 1, f"Function {p[1]} expects {len(func.input_types)} arguments but got {p.parser.num_args[-1]}")
            compiler_note(f"Error on Function '{p.parser.functions_handler.current_function.name}'")
            compiler_note("Called from Functions._call")
            sys.exit(1)
        if len(func.input_types) > 0 and func.input_types != p.parser.type_checker.stack[-len(func.input_types):]:
            compiler_error(p, 1, f"Function {p[1]} expects {func.input_types} but got {p.parser.type_checker.stack[-len(func.input_types):]}")
            compiler_note("Called from Functions._call")
            sys.exit(1)
        for _ in func.input_types:
            p.parser.type_checker.pop()
        if func.output_type is not None:
            p.parser.type_checker.push(func.output_type)

        p.parser.num_args.pop()
        out = ""
        if func.output_type is not None:
            out = std_message(["PUSHI -69"])
        out += p[3] + std_message([f"PUSHA {func.name.replace('_', '')}", "CALL", f"POP {len(func.input_types)}"])    # If the function exists, return the assembly code
        return out

    def _return(self, p):
        """
        return : RETURN expression
                | RETURN ';'
        """
        if p[2] != ";":
            expr = p.parser.type_checker.pop()
            if expr != p.parser.functions_handler.current_function.output_type:
                compiler_error(p, 1, f"Return type '{expr}' doesn't match function output type '{p.parser.functions_handler.current_function.output_type}'")
                compiler_note(f"Error on Function '{p.parser.functions_handler.current_function.name}'")
                compiler_note("Called from Functions._return")
                sys.exit(1)

            return p[2] + std_message([
                f"STOREL {-len(p.parser.functions_handler.current_function.input_types)-1}",
                "RETURN"])

        if p.parser.functions_handler.current_function.output_type is not None:
            compiler_error(p, 1, f"Return type '{p.parser.functions_handler.current_function.output_type}' doesn't match function output type 'None'")
            compiler_note(f"Error on Function '{p.parser.functions_handler.current_function.name}'")
            compiler_note("Called from Functions._return")
            sys.exit(1)

        return std_message(["RETURN"])

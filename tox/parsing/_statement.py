import sys

from tox import compiler_error, compiler_note,  std_message


class Print:
    """
    Hnadles the print statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "print": self._print,
            "multiple": self._multiple,
            "single": self._single,
            "empty": self._empty,
        }

    def handle(self, p, production) -> str:    # Calls the correct function based on the production
        return self.productions[production](p)

    def _print(self, p) -> str:
        """
        print : PRINT '(' multiple_prints ')'
        """
        return p[3] # Whatever the multiple_prints production returns

    def _multiple(self, p) -> str: # printing many things
        """
        multiple_prints : multiple_prints ',' expression
        """
        top = p.parser.type_checker.pop() # Get the top of the stack
        if top == "string": # If the top is a string, print it
            push_op = std_message(["WRITES"])
        elif top == "int": # If the top is an expression, print it
            push_op = std_message(["WRITEI"])

        return p[1] + p[3] + push_op # Whatever the multiple_prints production returns + the expression + the print operation

    def _single(self, p) -> str: # printing a single thing
        """
        multiple_prints : expression
        """
        top = p.parser.type_checker.pop() # Get the top of the stack<<
        if top == "string": # If the top is a string, print it
            push_op = std_message(["WRITES"])
        elif top == "int": # If the top is an expression, print it
            push_op = std_message(["WRITEI"])
        return p[1] + push_op # Whatever the expression production returns + the print operation

    def _empty(self, p) -> str: # printing nothing
        """
        multiple_prints : empty
        """
        return ""


class Assignment:
    """
    Handles the assignment statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "array_indexing": self._array_index,
            "variable": self._variable,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _array_index(self, p) -> str: # Assigning to an array index
        """
        assignment : ID '[' expression ']' ASSIGN expression
        """
        expr = p.parser.type_checker.pop()
        index = p.parser.type_checker.pop()
        id_meta, in_function, _ = p.parser.current_scope.get(p[1]) # Get the meta data of the variable
        if id_meta is None: # If the variable doesn't exist, report an error
            compiler_error(p, 1, f"Assignment to undeclared variable {p[1]}")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if not id_meta.type.startswith("&"):
            compiler_error(p, 1, f"Can't index to non array variable")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if index != 'int':
            compiler_error(p, 2, f"Can't index array with non integer value")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if id_meta.type[1:] != expr: # If the variable isn't an array, report an error
            compiler_error(p, 5, f"Assignment of '{expr}' to array of type '{id_meta.type}'")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)

        push_op = "PUSHGP" if not in_function else "PUSHFP" # Get the correct push operation
        return std_message([push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD", f"{p[3]}PADD", f"{p[6]}STORE 0"])

    def _variable(self, p) -> str: # Assigning to a variable
        """
        assignment : ID ASSIGN expression
        """
        expr = p.parser.type_checker.pop()
        id_meta, in_function, _ = p.parser.current_scope.get(p[1]) # Get the meta data of the variable
        if id_meta is None: # If the variable doesn't exist, report an error
            compiler_error(p, 1, f"Assignment to undeclared variable {p[1]}")
            compiler_note("Called from Assignment._expression")
            sys.exit(1)
        if id_meta.type.startswith("&"): # If the variable doesn't exist, report an error
            compiler_error(p, 1, f"Can't directly assign value to array. Try indexing.")
            compiler_note("Called from Assignment._expression")
            sys.exit(1)
        if id_meta.type != expr: # If the variable doesn't exist, report an error
            compiler_error(p, 1, f"Assignment of '{expr}' to variable of type '{id_meta.type}'")
            compiler_note("Called from Assignment._expression")
            sys.exit(1)
        
        store_op = "STOREG" if not in_function else "STOREL"    # Get the correct store operation
        return std_message([f"{p[3]}{store_op} {id_meta.stack_position[0]}"])


class Declaration:
    """
    Handles the declaration statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "array_declaration": self._array_declaration,
            "variable_declaration": self._variable_declaration,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _array_declaration(self, p) -> str: # Declaring 0 initialized array of size INT
        """
        declaration : ID ':' Vtype '[' INT ']' 
        """
        id_meta, _, _ = p.parser.current_scope.get(p[1]) # Get the meta data of the variable
        if id_meta is not None: # If the variable already exists, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from Declaration._array_declaration")
            sys.exit()
        else:
            if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+int(p[5])-1))
                p.parser.global_count += int(p[5])
            else:   # If the variable is declared in a function scope, add it to the function scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+int(p[5])-1))
                p.parser.frame_count += int(p[5])
            return std_message([f"PUSHN {int(p[5])}"])

    def _variable_declaration(self, p):
        """
        declaration : ID ':' type
        """
        if p[1] in p.parser.current_scope.Table: # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from Declaration._variable_declaration")
            sys.exit(1)
        else:
            if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count))
                p.parser.global_count += 1
            else:   # If the variable is declared in a function scope, add it to the function scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
                p.parser.frame_count += 1
            return std_message(["PUSHI 0"])


class DeclarationAssignment:
    """
    Handles the declaration assignment statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "array_literal_init": self._array_literal_init,
            "array_range_init": self._array_range_init,
            "variable_init": self._variable_init,
            "array_items": self._array_items,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _array_literal_init(self, p) -> str: # Declaring and initializing an array with a literal
        """
        declaration_assignment : ID ':' Vtype ASSIGN '[' arrayitems ']'
        """
        if p[1] in p.parser.current_scope.Table:    # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from DeclarationAssignment._array_literal_init")
            sys.exit(1)
        for i in range(p.parser.array_assign_items):
            item = p.parser.type_checker.pop()
            if item != p[3][1:]:
                compiler_error(p, 5, f"Initialization of array of type '{p[3]}' with item of type '{item}'. Look at item {p.parser.array_assign_items-i}")
                compiler_note("Called from DeclarationAssignment._array_literal_init")
                sys.exit(1)

        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+p.parser.array_assign_items-1))
            p.parser.global_count += p.parser.array_assign_items
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+p.parser.array_assign_items-1))
            p.parser.frame_count += p.parser.array_assign_items
        p.parser.array_assign_items = 0 # Reset the array assign items counter
        return p[6]

    def _array_range_init(self, p) -> str: # Declaring and initializing an array with a range
        """
        declaration_assignment : ID ':' Vtype ASSIGN '[' INT RETI INT ']'
        """
        if p[1] in p.parser.current_scope.Table:    # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from DeclarationAssignment._array_range_init")
            sys.exit(1)
        if p[3] != '&int':    # If the variable is not an integer array, report an error
            compiler_error(p, 1, f"Array of type {p[3]} cannot be initialized with a range")
            compiler_note("Called from DeclarationAssignment._array_range_init")
            sys.exit(1)

        start = int(p[6])
        end = int(p[8])
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+end-start))
            p.parser.global_count += end-start + 1
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+end-start))
            p.parser.frame_count += end-start + 1

            return std_message([f"PUSHI {i}" for i in range(start, end + 1)])

    def _variable_init(self, p) -> str:     # Declaring and initializing a variable
        """
        declaration_assignment : ID ':' type ASSIGN expression
        """
        expr = p.parser.type_checker.pop()
        if p[1] in p.parser.current_scope.Table:    # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Redeclaration of variable '{p[1]}'")
            compiler_note("Called from DeclarationAssignment._variable_init")
            sys.exit(1)
        if p[3] != expr:    # If the variable type and the expression type do not match, report an error
            compiler_error(p, 4, f"Initialization of variable of type '{p[3]}' with expression of type '{expr}'")
            compiler_note("Called from DeclarationAssignment._variable_init")
            sys.exit(1)

        else:
            if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count))
                p.parser.global_count += 1  # Increment the global count
            else:   # If the variable is declared in a function scope, add it to the function scope
                p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
                p.parser.frame_count += 1   # Increment the frame count

            return p[5]

    def _array_items(self, p) -> str:  # Handles the array items
        """
        arrayitems : arrayitems ',' expression
            | expression
        """
        p.parser.array_assign_items += 1    # Increment the array assign items counter
        if len(p) == 4:
            return p[1] + p[3]
        return p[1]


class If:
    """
    Handles the if statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "if": self._if,
            "else_if": self._else_if,
            "else": self._else,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _if(self, p) -> str:
        """
        if : IF expression ss '{' stmts '}' es else_if
        """
        expr = p.parser.type_checker.pop()
        if expr != 'int': #NOTE: Later we could add support for bools
            compiler_error(p, 1, f"Condition type must be 'int', not '{expr}'")
            compiler_note("Called from If._if")
            sys.exit(1)

        current_if_count = p.parser.if_count                        # Get the current if count
        out = p[2]                                                  # Push condition to the stack
        out += std_message([f"JZ IFLABEL{current_if_count}END"])    # Jump to the end label if the expression is false
        out += p[5]                                                 # Push the statements
        out += p[7]                                                 # Get out of if scope
        out += std_message([f"JUMP FINISHIF{p.parser.rel_if_count}"])  # Skip the else if statements
        out += std_message([f"IFLABEL{current_if_count}END:"])      # Add the end label
        out += p[8]                                                 # Push the else if statements
        p.parser.if_count += 1                                      # Increment the if count

        return out

    def _else_if(self, p) -> str:
        """
        else_if : ELSE IF expression ss '{' stmts '}' es else_if
                | else
        """
        if len(p) == 2:
            return p[1] # There is no else if

        expr = p.parser.type_checker.pop()
        if expr != 'int':
            compiler_error(p, 2, f"Condition type must be 'int', not '{expr}'")
            compiler_note("Called from If._if_else")
            sys.exit(1)

        current_if_count = p.parser.if_count                                # Get the current if count
        out = p[3]                                                          # Push condition to the stack
        out += std_message([f"JZ ELSEIFLABEL{current_if_count}END"])        # Jump to the end of this else if if the expression is false
        out += p[6]                                                         # Push the statements
        out += p[8]                                                         # Get out of else if scope
        out += std_message([f"JUMP FINISHIF{p.parser.rel_if_count}"])       # Skip the else if statements
        out += std_message([f"ELSEIFLABEL{current_if_count}END:"])          # Add the end else if label
        out += p[9]                                                         # Push the else if statements
        p.parser.if_count += 1                                              # Increment the if count


        return out

    def _else(self, p) -> str:
        """
        else : ELSE ss '{' stmts '}' es
            |
        """
        p.parser.rel_if_count += 1                  # Increment the relative if count
        if len(p) == 1: return std_message([f"FINISHIF{p.parser.rel_if_count}:"])    # If there is no else, return an empty string

        current_if_count = p.parser.if_count                            # Get the current if count
        out = p[4]                                                      # Push the statements
        out += p[6]                                                     # Get out of else scope
        out += std_message([f"ELSELABEL{current_if_count}END:"])        # Add the end if label
        out += std_message([f"FINISHIF{p.parser.rel_if_count}:"])       # Add the finish if label
        p.parser.if_count += 1                                          # Increment the if count

        return out


class Loop:
    """
    Handles the loop statements.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "while": self._while,
            "do_while": self._do_while,
            "for": self._for,
            "for_updates": self.__for_updates,
            "for_update": self.__for_update,
            "for_inits": self.__for_inits,
            "for_init": self.__for_init,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _while(self, p) -> str:
        """
        while : WHILE expression ss '{' stmts '}' es
        """
        expr = p.parser.type_checker.pop()
        if expr != 'int':
            compiler_error(p, 1, f"Condition type must be 'int', not '{expr}'")
            compiler_note("Called from Loop._while")
            sys.exit(1)

        current_while_count = p.parser.loop_count
        out = std_message([f"LOOP{current_while_count}START:"])             # Start of the while loop
        out += p[2]                                                         # Condition
        out += std_message([f"JZ LOOP{current_while_count}END"])            # End of the while loop
        out += p[5]                                                         # Perform the statements
        out += p[7]                                                         # Close the scope
        out += std_message([f"JUMP LOOP{current_while_count}START"])        # Jump to start of the while loop
        out += std_message([f"LOOP{current_while_count}END:"])              # End of the while loop
        p.parser.loop_count += 1                                            # Increment the loop count
        p.parser.current_loops.pop()                                        # Pop the current loop off the stack

        return out

    def _do_while(self, p) -> str:
        """
        do_while : DO ss '{' stmts '}' es WHILE '(' expression ')'
        """
        expr = p.parser.type_checker.pop()
        if expr != 'int':
            compiler_error(p, 1, f"Condition type must be 'int', not '{expr}'")
            compiler_note("Called from Loop._do_while")
            sys.exit(1)

        current_do_while_count = p.parser.loop_count
        out = std_message([f"LOOP{current_do_while_count}START:"])          # Start of the do while loop
        out += p[4]                                                         # Perform the statements
        out += p[6]                                                         # Close the scope
        out += p[9]                                                         # Condition
        out += std_message([f"JZ LOOP{current_do_while_count}END"])         # Jump to end of do while loop if condition is false
        out += std_message([f"JUMP LOOP{current_do_while_count}START"])     # Jump to start of do while loop
        out += std_message([f"LOOP{current_do_while_count}END:"])           # End of the do while loop
        p.parser.loop_count += 1                                            # Increment the loop count
        p.parser.current_loops.pop()                                        # Pop the current loop off the stack

        return out

    def _for(self, p) -> str:
        """
        for : FOR ss '(' for_inits ';' expression ';' for_updates ')' ss '{' stmts  '}' es es
        """
        expr = p.parser.type_checker.pop()
        if expr != 'int':
            compiler_error(p, 1, f"Condition type must be 'int', not '{expr}'")
            compiler_note("Called from Loop._for")
            sys.exit(1)

        current_for = p.parser.loop_count
        out =  p[4]                                             # Perform the for_inits
        out += std_message([f"LOOP{current_for}START:"])        # Start of the for loop
        out += p[6]                                             # Condition
        out += std_message([f"JZ LOOP{current_for}END"])        # Jump to end of for loop if condition is false
        out += p[12]                                            # Execute the for loop
        out += p[8]                                             # Perform the for_updates
        out += p[14]                                            # Close the for_inner scope             
        out += std_message([f"JUMP LOOP{current_for}START"])    # Jump back to the start of the for loop
        out += std_message([f"LOOP{current_for}END:"])          # End of the for loop
        out += p[15]                                            # Close the for_outer scope
        p.parser.loop_count += 1                                # Increment the loop count
        p.parser.current_loops.pop()                            # Pop the current loop off the stack

        return out

    def __for_updates(self, p) -> str: # Handle all the for updates
        """
        for_updates : for_updates ',' for_update
                | for_update
        """
        if len(p) == 4:
            return p[1] + p[3]
        else:
            return p[1]

    def __for_update(self, p) -> str:
        """
        for_update : assignment
        """
        return p[1]

    def __for_inits(self, p) -> str: # Handle all the for inits
        """
        for_inits : for_inits ',' for_init
            | for_init
        """
        if len(p) == 4:
            return p[1] + p[3]
        else:
            return p[1]

    def __for_init(self, p) -> str:
        """
        for_init : declaration_assignment
            | declaration
            | assignment
            |
        """
        if len(p) == 2:
            return p[1]
        else:
            return ""


class BreakContinue:
    """
    Handles the break and continue statements.
    """
    def __init__(self):
        self.productions = {        # All the productions that this class handles
            "break": self._break,
            "continue": self._continue
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _break(self, p) -> str: # Handle the break statement
        if len(p.parser.current_loops) == 0:
            compiler_error(p, 1, "'break' statement not allowed outside of a loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)

        return std_message([f"JUMP LOOP{p.parser.loop_count}END"])

    def _continue(self, p) -> str: # Handle the continue statement
        if len(p.parser.current_loops) == 0:
            compiler_error(p, 1, "'continue' statement not allowed outside of a loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)
        if p.parser.current_loops[-1] == "DO":
            compiler_error(p, 1, "'continue' statement not allowed inside of do-while loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)

        return std_message([f"JUMP LOOP{p.parser.loop_count}START"])
import sys

from lat import compiler_error, compiler_note,  std_message


class IO:
    """
    Hnadles the print statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "print": self._print,
            "multiple": self._multiple,
            "single": self._single,
            "empty": self._empty,
            "read": self._read,
            "read_type": self._read_type,
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
        if top == "filum": # If the top is a filum, print it
            push_op = std_message(["WRITES"])
        elif top == "integer": # If the top is an expression, print it
            push_op = std_message(["WRITEI"])
        elif top == "float": # If the top is an expression, print it
            push_op = std_message(["WRITEF"])
        elif top.startswith("&"):
            compiler_error(p, 2, f"Can't print array. Not implemented yet.")
            compiler_note("Called from Print._single")
            sys.exit(1)

        return p[1] + p[3] + push_op # Whatever the multiple_prints production returns + the expression + the print operation

    def _single(self, p) -> str: # printing a single thing
        """
        multiple_prints : expression
        """
        top = p.parser.type_checker.pop() # Get the top of the stack<<
        if top == "filum": # If the top is a filum, print it
            push_op = std_message(["WRITES"])
        elif top == "integer": # If the top is an expression, print it
            push_op = std_message(["WRITEI"])
        elif top == "float": # If the top is an expression, print it
            push_op = std_message(["WRITEF"])
        elif top.startswith("&"):
            compiler_error(p, 1, f"Can't print array. Not implemented yet.")
            compiler_note("Called from Print._single")
            sys.exit(1)
        return p[1] + push_op # Whatever the expression production returns + the print operation

    def _empty(self, p) -> str: # printing nothing
        """
        multiple_prints :
        """
        return ""

    def _read(self, p):
        """
        read : read_type '(' multiple_prints ')'
        """
        return p[3] + std_message(["READ"]) + p[1]

    def _read_type(self, p):
        """
        read_type : READ_INT
                | READ_FLOAT
                | READ_STRING
        """
        if p[1][-1] == "i":
            p.parser.type_checker.push("integer")
            push_op = std_message(["ATOI"])
        elif p[1][-1] == "f":
            p.parser.type_checker.push("float")
            push_op = std_message(["ATOF"])
        elif p[1][-1] == "s":
            p.parser.type_checker.push("filum")
            push_op = std_message([""])
        return push_op


class Assignment:
    """
    Handles the assignment statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "indexing": self._indexing,
            "variable": self._variable,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _indexing(self, p) -> str: # Assigning to an array or pointer index
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
        if not id_meta.type.startswith("vec") and not id_meta.type.startswith("&"):
            compiler_error(p, 1, f"Indexing not allowed on variable of type '{id_meta.type}'")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if index != 'integer':
            compiler_error(p, 2, f"Indexing with non-integer type '{index}'")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if id_meta.type[1:] != expr and id_meta.type[4:-1] != expr:
            compiler_error(p, 5, f"Assignment of '{expr}' to variable of type '{id_meta.type}'")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)

        push_op = "PUSHGP" if not in_function else "PUSHFP" # Get the correct push operation
        if id_meta.type.startswith("vec"):
            return std_message([push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD", f"{p[3]}PADD", f"{p[6]}STORE 0"])
        elif id_meta.type.startswith("&"):
            return std_message([push_op, f"LOAD {id_meta.stack_position[0]}", f"{p[3]}PADD", f"{p[6]}STORE 0"])

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
        if id_meta.type.startswith("vec"):
            compiler_error(p, 1, f"Assignment to array not allowed. Use indexing instead.")
            compiler_note("Called from Assignment._expression")
            sys.exit(1)
        if id_meta.type.startswith("&") and expr.startswith("vec") and id_meta.type[1:] == expr[4:-1]:
            pass # If ID is of type &T and expr is of type vec<T>, then it's fine
        elif id_meta.type != expr: # If the types don't match, report an error
            compiler_error(p, 1, f"Assignment of '{expr}' to variable of type '{id_meta.type}'")
            compiler_note("Called from Assignment._variable")
            sys.exit(1)

        store_op = "STOREG" if not in_function else "STOREL"    # Get the correct store operation
        return std_message([f"{p[3]}{store_op} {id_meta.stack_position[0]}"])


class Declaration:
    """
    Handles the declaration statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "variable_declaration": self._variable_declaration,
            "pointer_declaration": self._pointer_declaration,
            "array_declaration": self._array_declaration,
        }

    def handle(self, p, production) -> str:
        return self.productions[production](p)

    def _variable_declaration(self, p):
        """
        declaration : ID ':' type
        """
        if p[1] in p.parser.current_scope.Table: # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from Declaration._variable_declaration")
            sys.exit(1)

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count))
            p.parser.global_count += 1
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
            p.parser.frame_count += 1

        if p[3] == 'integer':
            return std_message(["PUSHI 0"])
        elif p[3] == 'float':
            return std_message(["PUSHF 0.0"])
        elif p[3] == 'filum':
            return std_message(["PUSHS ''"])

    def _pointer_declaration(self, p):
        """
        declaration : ID ':' Ptype
        """
        if p[1] in p.parser.current_scope.Table:
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from Declaration._pointer_declaration")
            sys.exit(1)

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            push_op = std_message(["PUSHGP", f"PUSHI {p.parser.global_count}", "PADD"]) # Get the correct push operation
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count), False)
            p.parser.global_count += 1
        else:   # If the variable is declared in a function scope, add it to the function scope
            push_op = std_message(["PUSHFP", f"PUSHI {p.parser.frame_count}", "PADD"]) # Get the correct push operation
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count), False)
            p.parser.frame_count += 1

        # Uninitialized pointers point to themselves
        if p[3] == '&integer':
            return push_op
        elif p[3] == '&float':
            return push_op
        elif p[3] == '&filum':
            return push_op

    def _array_declaration(self, p) -> str: # Declaring 0 initialized array of size integer
        """
        declaration : ID ':' Vtype '[' integer ']'
        """
        if p[1] in p.parser.current_scope.Table:
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from Declaration._array_declaration")
            sys.exit()

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+int(p[5])-1))
            p.parser.global_count += int(p[5])
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+int(p[5])-1))
            p.parser.frame_count += int(p[5])

        if p[3] == 'vec<integer>':
            return std_message([f"PUSHN {int(p[5])}"])
        elif p[3] == 'vec<float>':
            return std_message([f"PUSHF 0.0" for i in range(int(p[5]))])
        elif p[3] == 'vec<filum>':
            return std_message([f"PUSHS ''" for i in range(int(p[5]))])
        assert False, "Invalid type in Declaration._array_declaration"


class DeclarationAssignment:
    """
    Handles the declaration assignment statement.
    """
    def __init__(self):
        self.productions = {    # All the productions that this class handles
            "array_literal_init": self._array_literal_init,
            "array_range_init": self._array_range_init,
            "pointer_init": self._pointer_init,
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
            if item != p[3][4:-1]:
                compiler_error(p, 5, f"Initialization of array of type '{p[3]}' with item of type '{item}'. Look at item {p.parser.array_assign_items-i}")
                compiler_note("Called from DeclarationAssignment._array_literal_init")
                sys.exit(1)

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+p.parser.array_assign_items-1))
            p.parser.global_count += p.parser.array_assign_items
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+p.parser.array_assign_items-1))
            p.parser.frame_count += p.parser.array_assign_items
        p.parser.array_assign_items = 0 # Reset the array assign items counter
        return p[6]

    def _array_range_init(self, p) -> str: # Declaring and initializing an array with a range TODO: turn integer into expression if possible
        """
        declaration_assignment : ID ':' Ptype ASSIGN '['   integer RETI   integer ']'
        """
        if p[1] in p.parser.current_scope.Table:    # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from DeclarationAssignment._array_range_init")
            sys.exit(1)
        if p[3] != 'vec<integer>':    # If the variable is not an integer array, report an error
            compiler_error(p, 1, f"Array of type '{p[3]}' cannot be initialized with a range")
            compiler_note("Called from DeclarationAssignment._array_range_init")
            sys.exit(1)

        start = int(p[6])
        end = int(p[8])
        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:   # If the variable is declared in the global scope, add it to the global scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count+end-start))
            p.parser.global_count += end-start + 1
        else:   # If the variable is declared in a function scope, add it to the function scope
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count+end-start))
            p.parser.frame_count += end-start + 1

            return std_message([f"PUSHI {i}" for i in range(start, end + 1)])

    def _pointer_init(self, p) -> str: # Declaring and initializing a pointer
        """
        declaration_assignment : ID ':' Ptype ASSIGN expression
        """
        expr = p.parser.type_checker.pop()
        if p[1] in p.parser.current_scope.Table:    # If the variable already exists in the current scope table, report an error
            compiler_error(p, 1, f"Variable {p[1]} is already defined")
            compiler_note("Called from DeclarationAssignment._pointer_init")
            sys.exit(1)
        if not expr.startswith("vec") and expr != p[3]: # Cam only assign vectors and pointers to pointer
            compiler_error(p, 5, f"Initialization of pointer of type '{p[3]}' with expression of type '{expr}'")
            compiler_note("Called from DeclarationAssignment._pointer_init")
            sys.exit(1)

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
        if p.parser.current_scope.level == 0:
            p.parser.current_scope.add(p[1], p[3], (p.parser.global_count, p.parser.global_count))
            p.parser.global_count += 1
        else:
            p.parser.current_scope.add(p[1], p[3], (p.parser.frame_count, p.parser.frame_count))
            p.parser.frame_count += 1

        return p[5]

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

        p[3] = p[3].replace(" ", "") # Remove the spaces from the type
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
        if expr != 'integer':
            compiler_error(p, 1, f"Condition type must be 'integer', not '{expr}'")
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
        if expr != 'integer':
            compiler_error(p, 2, f"Condition type must be 'integer', not '{expr}'")
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
        p.parser.rel_if_count += 1                                      # Increment the relative if count
        if len(p) == 1: return std_message([f"FINISHIF{p.parser.rel_if_count}:"])    # If there is no else, return an empty filum

        current_if_count = p.parser.if_count                            # Get the current if count
        out = p[4]                                                      # Push the statements
        out += p[6]                                                     # Get out of else scope
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
        while : loop_while expression ss '{' stmts '}' es
        """
        expr = p.parser.type_checker.pop()
        if expr != 'integer':
            compiler_error(p, 1, f"Condition type must be 'integer', not '{expr}'")
            compiler_note("Called from Loop._while")
            sys.exit(1)

        current_while_count = p.parser.loop_count
        out = std_message([f"LOOP{current_while_count}START:"])             # Start of the while loop
        out += p[2]                                                         # Condition
        out += std_message([f"JZ LOOP{current_while_count}END"])            # End of the while loop
        out += p[5]                                                         # Perform the statements
        out += std_message([f"NEXTLOOP{current_while_count}:"])
        out += p[7]                                                         # Close the scope
        out += std_message([f"JUMP LOOP{current_while_count}START"])        # Jump to start of the while loop
        out += std_message([f"LOOP{current_while_count}END:"])              # End of the while loop
        p.parser.loop_count += 1                                            # Increment the loop count
        p.parser.current_loops.pop()                                        # Pop the current loop off the stack

        return out

    def _do_while(self, p) -> str:
        """
        do_while : loop_do ss '{' stmts '}' es WHILE '(' expression ')'
        """
        expr = p.parser.type_checker.pop()
        if expr != 'integer':
            compiler_error(p, 1, f"Condition type must be 'integer', not '{expr}'")
            compiler_note("Called from Loop._do_while")
            sys.exit(1)

        current_do_while_count = p.parser.loop_count
        out = std_message([f"LOOP{current_do_while_count}START:"])          # Start of the do while loop
        out += p[4]                                                         # Perform the statements
        out += std_message([f"NEXTLOOP{current_do_while_count}:"])          # Next loop label (continue statement jumps here)
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
        for : loop_for ss '(' for_inits ';' expression ';' for_updates ')' ss '{' stmts  '}' es es
        """
        expr = p.parser.type_checker.pop()
        if expr != 'integer':
            compiler_error(p, 1, f"Condition type must be 'integer', not '{expr}'")
            compiler_note("Called from Loop._for")
            sys.exit(1)

        current_for = p.parser.loop_count
        out =  p[4]                                             # Perform the for_inits
        out += std_message([f"LOOP{current_for}START:"])        # Start of the for loop
        out += p[6]                                             # Condition
        out += std_message([f"JZ LOOP{current_for}END"])        # Jump to end of for loop if condition is false
        out += p[12]                                            # Execute the for loop
        out += std_message([f"NEXTLOOP{current_for}:"])         # Next loop label (continue statements jump here)
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
        """
        break : BREAK
        """
        if len(p.parser.current_loops) == 0:
            compiler_error(p, 1, "'break' statement not allowed outside of a loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)

        return std_message([f"JUMP LOOP{p.parser.loop_count}END"])

    def _continue(self, p) -> str: # Handle the continue statement
        """
        continue : CONTINUE
        """
        if len(p.parser.current_loops) == 0:
            compiler_error(p, 1, "'continue' statement not allowed outside of a loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)
        if p.parser.current_loops[-1] == "DO":
            compiler_error(p, 1, "'continue' statement not allowed inside of do-while loop")
            compiler_note("Called from BreakContinue._break.")
            sys.exit(1)

        return std_message([f"JUMP NEXTLOOP{p.parser.loop_count}"])
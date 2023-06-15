Lexical and Syntax Analyzer Documentation
                                                                      **Lexical Analyzer**
The lexical analyzer is responsible for tokenizing the input program. It recognizes individual tokens by matching them with their corresponding regular expressions. Here are the tokens and their regular expressions used in the code:

while: Matches the keyword "while".
self: Matches the keyword "self".
for: Matches the keyword "for".
print: Matches the keyword "print".
if: Matches the keyword "if".
elif: Matches the keyword "elif".
else: Matches the keyword "else".
class: Matches the keyword "class".
function_call: Matches the keyword "function_call".
inc: Matches the keyword "inc".
dec: Matches the keyword "dec".
def: Matches the keyword "def".
return: Matches the keyword "return".
identifier: Matches any sequence of alphabetic characters (a-z, A-Z) or underscores followed by any sequence of alphanumeric characters or underscores.
object_call: Matches the keyword "object_call".
add: Matches the addition operator "+".
sub: Matches the subtraction operator "-".
mul: Matches the multiplication operator "*".
div: Matches the division operator "/".
end: Matches the keyword "end".
The lexical analyzer code reads the input program and generates a sequence of tokens, each token consisting of a type and a value.

                                                                    **Syntax Analyzer**
The syntax analyzer is responsible for parsing the tokens generated by the lexical analyzer according to the defined grammar rules. It determines the structure of the program and ensures that it conforms to the specified syntax.

The parse_statement function serves as the main entry point for parsing statements. It takes the tokens and the current index as input and selects the appropriate parsing function based on the token type.

parse_while_loop: Parses a while loop statement.
class_body_values: Parses a statement involving the self keyword.
parse_for_loop: Parses a for loop statement.
parse_print_statement: Parses a print statement.
parse_if_condition: Parses an if condition statement.
parse_elif_condition: Parses an elif condition statement.
parse_else_condition: Parses an else condition statement.
parse_class_statement: Parses a class statement.
parse_function_call: Parses a function call statement.
parse_inc_dec_statement: Parses an increment or decrement statement.
parse_function: Parses a function definition statement.
parse_return_statement: Parses a return statement.
parse_assignment_statement: Parses an assignment statement.
parse_object_call: Parses an object call statement.
parse_operators: Parses an expression involving arithmetic operators.
If none of the token types match the above conditions, it indicates an invalid statement, and a SyntaxError is raised.

The code also checks for the presence of the end keyword at the end of the program. If it is missing, an error is raised indicating that the program should end with the end keyword.

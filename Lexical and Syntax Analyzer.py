import re
import nltk
import sys
import traceback

class SymbolTable:
    def __init__(self):
        self.table = {}

    def add_symbol(self, name, type):
        if name not in self.table:
            self.table[name] = type

    def print_table(self):
        for name, type in self.table.items():
            print(f"{name} -> {type}")


class Node:
    def __init__(self, line_num, token_id, lexeme, token_type, class_type):
        self.line_num = line_num
        self.token_id = token_id
        self.lexeme = lexeme
        self.token_type = token_type
        self.class_type = class_type
        self.next = None

    def __iter__(self):
        return iter((self.line_num, self.token_id, self.lexeme, self.token_type, self.class_type))


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_node(self, lexeme, token_type, line_number, symbol_table):
        new_node = Node(line_number, len(symbol_table.table),
                        lexeme, token_type, None)

        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node

        self.tail = new_node

        if token_type == "identifier":
            symbol_table.add_symbol(lexeme, "undefined")

    def print_list(self):
        current_node = self.head
        while current_node is not None:
            print(current_node.lexeme, "->", (" "), current_node.token_type,
                  (" "), "->", "Line", current_node.line_num)
            current_node = current_node.next


# Define regular expressions for each token
datatypes_RE = r'\b(int|float|bool)\b'
keywords_RE = r'\b(while|__init__|else|if|elif|input|print|return|def|class|self|in|range)\b'
identifier_RE = r'\b[a-zA-Z_]\w*\b'
numerals_RE = r'[0-9]+[+-]'
flt_numeral_RE = r'[+-]?[0-9]+\.[0-9]+'
#special_characters_RE = r'[*<,>:\']'

# Define a list of tuples to store the token pattern and its corresponding type

token_patterns = [
    (r'<', 'less', 'operator'),
    (r'\n', 'newline', 'separator'),
    (r'end', 'end', 'keyword'),
    (r'\t', 'tab', 'separator'),
    (r'>', 'gt', 'operator'),
    (r'\badd\b', 'add', 'operator'),
    (r'\bsub\b', 'sub', 'operator'),
    (r'\bmul\b', 'mul', 'operator'),
    (r'\bdiv\b', 'div', 'operator'),
    (r'\bmod\b', 'mod', 'operator'),
    (r'<=', 'lesseq', 'operator'),
    (r'>=', 'gteq', 'operator'),
    (r'==', 'eq', 'operator'),
    (r'!=', 'noteq', 'operator'),
    (r':', 'colon', 'separator'),
    (r'\bint\b', 'int', 'datatype'),
    (r'\bfloat\b', 'float', 'datatype'),
    (r'\bbool\b', 'bool', 'datatype'),
    (r'\bif\b', 'if', None),
    (r'\belif\b', 'elif', None),
    (r'"', 'double quote', 'delimiter'),
    (r'\belse\b', 'else', None),
    (r'\bwhile\b', 'while', None),
    (r'\bfor\b', 'for', None),
    (r'\breturn\b','return', None),
    (r'\bdef\b', 'def', None),
    #(r'\.', 'dot', 'operator'),
    (r'\bthis.\b', 'this.', None),
    (r'\bfunction_call\b','function_call', None),
    (r'\bobject_call\b','object_call', None),
    (r'\bprint\b', 'print', None),
    (r'\binput\b', 'input', None),
    (r'\bself\b', 'self', None),
    (r'\bin\b', 'in', None),
    (r'\brange\b', 'range', None),
    (r'\bclass\b', 'class', None),
    (r'\b__init__\b', '__init__', None),
    (r'\+\+', 'inc', None),
    (r'--', 'dec', None),
    (identifier_RE, 'identifier', 'identifier'),
    (numerals_RE, 'numeral', 'literal'),
    (flt_numeral_RE, 'flt_numeral', 'literal'),
    #(special_characters_RE, 'special_char', None),
    (r'\+', 'operator', 'operator'),
    (r'-', 'operator', 'operator'),
    (r'\*', 'operator', 'operator'),
    (r'/', 'operator', 'operator'),
    (r'%', 'operator', 'operator'),
    (r'=', 'assignment_operator', 'operator'),
    (r'\(', 'lparen', 'separator'),
    (r'\)', 'rparen', 'separator'),
    (r'{', 'l_brace', 'separator'),
    (r'}', 'r_brace', 'separator'),
    (r'\[', 'l_bracket', 'separator'),
    (r']', 'r_bracket', 'separator'),
    (r',', 'comma', 'separator'),
    (r'\'', 'apostrophe', 'delimiter'),
    (r'[()\[\]{}]', 'bracket', 'separator'),
    (r'\n', 'newline', 'separator'),
    (r'\s+', None, None),
    (r'\.', 'dot', 'delimiter'),
    (r"\n", None, None),
    (r"[+\-*/=<>!%&|?^~:;,.(){}\[\]@#]", None, None),
    (r'<', 'operator', 'operator'),
    (r'>', 'operator', 'operator'),
    (r'==', 'operator', 'operator'),
    (r'<=', 'operator', 'operator'),
    (r'>=', 'operator', 'operator'),
    (r'!=', 'operator', 'operator'),
    (r'true', 'boolean', 'literal'),
    (r'false', 'boolean', 'literal'),
    (r"'(?:\\.|[^'])*'", 'string', 'literal'),
    (r'"(?:\\.|[^"])*"', 'string', 'literal'),

]


class Token:
    def __init__(self, id, value, type, class_type, line_number):
        self.id = id
        self.value = value
        self.type = type
        self.class_type = class_type
        self.line_number = line_number

    def __str__(self):
        return f"{self.value} ({self.id}, {self.value}, {self.type}, {self.class_type}, {self.line_number})"

        ### new###


def tokenize(code_input):
    tokens = []
    id_counter = 0
    inside_quotes = False
    quote_char = None
    quote_start = None
    symbol_table = SymbolTable()
    linked_list = LinkedList()
    for line_number, line in enumerate(code_input.split("\n"), 1):
        line = line.strip()
        if not line:
            continue
        while line:
            if inside_quotes:
                match = re.search(
                    rf"[^{quote_char}\\]+(?:\\.[^{quote_char}\\]+)*{quote_char}", line)
                if match:
                    lexeme = match.group(0)
                    id_counter += 1
                    token = Token(id_counter, lexeme,
                                  "string_literal", "literal", line_number)
                    tokens.append(token)
                    linked_list.add_node(
                        lexeme, "string_literal", line_number, symbol_table)
                    line = line[match.end():].lstrip()
                    inside_quotes = False
                    quote_char = None
                else:
                    invalid_literal = line[quote_start:]
                    print(
                        f"Invalid string literal: {invalid_literal} at line number {line_number}")
                    line = ""
            else:
                match = None
                for pattern, token_type, class_type in token_patterns:
                    match = re.match(pattern, line)
                    if match:
                        lexeme = match.group(0)
                        id_counter += 1
                        token = Token(id_counter, lexeme,
                                      token_type, class_type, line_number)
                        tokens.append(token)
                        linked_list.add_node(
                            lexeme, token_type, line_number, symbol_table)
                        symbol_table.add_symbol(lexeme, "undefined")
                        line = line[match.end():].lstrip()
                        break
                if not match:
                    invalid_char = re.match(r'\S', line)
                    if invalid_char:
                        print(
                            f"Invalid character: {invalid_char.group(0)} at line number {line_number}")
                    line = ""
                elif match.group(0) in ['"', "'"]:
                    inside_quotes = True
                    quote_char = match.group(0)
                    quote_start = len(line) - len(line.lstrip(quote_char))
    linked_list.print_list()
    print("\n")
    return tokens


# Test the function
c = open(r'c:\\Users\\musab\Downloads\\main cc\\Lexical Analyzer\\COMPILER\\COMPILERRRRRR\\InputProgForPythonCode.PY')
code_input = c.read()
count = 0


def remove_Spaces(code_input):
    scan = []
    for line in code_input:
        if (line.strip() != ''):
            scan.append(line.strip())
    return scan


def remove_Comments(code):

    code = re.sub(r"#[^\n]*", "", code)

    code = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
                  "", code, flags=re.DOTALL)

    return code


print("\n")
print("\n")
program_Comments_removed = remove_Comments(code_input)
prog = program_Comments_removed.split('\n')

scanned_Prog = remove_Spaces(prog)

scan = '\n'.join([str(elem) for elem in scanned_Prog])
scanned_Program_lines = scan.split('\n')
match_counter = 0

Source_Code = []
for line in scanned_Program_lines:
    Source_Code.append(line)

display_counter = 0
Source_Code = code_input.split("\n")
for line in Source_Code:
    count = count + 1
    print("line#", count, "\n", line)
    tokens = []
    for token in nltk.wordpunct_tokenize(line):
        if token.strip():
            tokens.append(token)
    print("Tokens are ", tokens)
    print("\n")
    code_tokens = nltk.wordpunct_tokenize(code_input)
print("All tokens are: \n", code_tokens, "\n")
tokens = tokenize(code_input)

print("\tThe output is in the order of The Tokens (Token Number, Token Class, Token Type, Line Number)\t")
print("\n")
for token in tokens:
    print("\t", str(token), end='  ')
    print('\n')


index = 0
token = tokens[index]

def parse_program(tokens, index):
    try:
        parse_statement(tokens, index)
        print("\n\t\t\tPARSED SUCCESSFULLY\t\t\t\n")
   
    except SyntaxError as e:
        print("\n\t\t\tSYNTAX ERROR\t\t\t\n")
    
    except IndexError:
        print("\n\t\t\tSYNTAX ERROR\t\t\t\n")
        print("Error: Make sure the program ends with 'end'")
         
# Helper function to parse a statement
def parse_statement(tokens,index):
    token = tokens[index]
    if token.type == 'while':
        return parse_while_loop(tokens,index)
    elif token.type == 'self':
        return class_body_values(tokens,index)
    if token.type == 'for':
        return parse_for_loop(tokens,index)
    elif token.type == 'print':
        return parse_print_statement(tokens,index)
    elif token.type == 'if':
        return parse_if_condition(tokens, index)
    elif token.type == 'elif':
        return parse_elif_condition(tokens, index)
    elif token.type == 'else':
        return parse_else_condition(tokens, index)
    elif token.type == 'class':
        return parse_class_statement(tokens, index)
    elif token.type == 'function_call':
        return parse_function_call(tokens,index)
    if token.type == 'inc' or token.type == 'dec':
        return parse_inc_dec_statement(tokens,index)
    elif token.type == 'def':
        return parse_function(tokens,index)
    elif token.type == 'return':
        return parse_return_statement(tokens,index)
    elif token.type == 'identifier' :
        return parse_assignment_statement(tokens,index)
    elif token.type== 'object_call':
        return parse_object_call(tokens,index)
    elif token.type == 'add' or token.type =='sub' or token.type == 'mul' or token.type == 'div':
        return parse_operators(tokens,index)
    elif token.type == 'end':
        print("Parsed successfully")
        sys.exit()
    else:
        # Handle error: Invalid statement
        raise SyntaxError("\nInvalid statement\n")

# Parse a single statement

def parse_single_statement(tokens,index):
   
    if index>= len(tokens):
        return None
    
    token = tokens[index]  
    if token.type == 'while' or token.type == 'if' or token.type == 'for' or token.type == 'print' or token.type== 'function_call' or token.type == 'inc' or \
        token.type == 'elif' or token.type== 'else' or token.type == 'input' or token.type == 'return' or token.type =='self' or token.type == 'identifier' or token.type == 'end' or\
        token.type == 'object_call' or token.type=='class' or token.type== 'dec' or token.type == 'def' or token.type == 'identifier' or token.type == 'add' or token.type =='sub' or token.type == 'mul' or token.type == 'div' :   
        return parse_statement(tokens,index)
    else:
        # Handle error: Invalid statement
        raise SyntaxError("Invalid statement")


# Parse a body
def parse_body(tokens,index):
    
    token = tokens[index]
    print("In Parsing Body")
    print(index, token)
    if token.type == 'while' or token.type == 'if' or token.type == 'for' or token.type == 'print' or token.type== 'function_call' or token.type == 'inc' or \
        token.type == 'elif' or token.type== 'else' or token.type == 'input' or token.type == 'return' or token.type =='self' or token.type == 'identifier' or token.type == 'end' or\
        token.type == 'object_call' or token.type == 'class' or token.type== 'dec' or token.type == 'def' or token.type == 'identifier' or token.type == 'add' or token.type =='sub' or token.type == 'mul' or token.type == 'div' :
        return parse_single_statement(tokens,index)
    if index >= len(tokens):
    
        return None
    else:
        # Handle error: Invalid body
        raise SyntaxError("Invalid body")


# Parse a while loop
def parse_while_loop(tokens,index):
    print("Parsing while loop")
    token = tokens[index]
    print(index, token)
    if token.type == 'while':
        print("Parsing condition")
        index = index + 1
        token = tokens[index]
        token, index  = parse_condition(tokens,index)
        
        print(index, token)
        
        if token.type == 'colon':
                print("Parsing body")
                print(index, token)
                index += 1
                token = tokens[index]
                print("index is", index)
                if token.type == 'newline':
                    index += 1
                print(index, token)
                while tokens[index].type == 'newline':
                    index += 1
                    token = tokens[index]
                token , index = parse_body(tokens, index)
        else:
            # Handle error: Expected ':'
            raise SyntaxError("Expected ':' after while condition")
    else:
        # Handle error: Invalid while loop
        raise SyntaxError("Invalid while loop")


# Parse a condition
def parse_condition(tokens,index):
    print("Parsing inside condition")
    token = tokens[index]
    print(index, token)
    if token.type == 'identifier' or token.type == 'numeral':
        print("Parsing expression condition1")
        index = index +1
        token = tokens[index]
        print(index, token)
        if token.type == 'less' or token.type == 'gt':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'assignment_operator':
                index += 1
                token = tokens[index]
                print("ahh")
                print(index, token)
                if token.type == 'identifier'or token.type=='numeral':
                    print("Parsing expression condition2")
                    index = index +1
                    token = tokens[index]
                    print(index, token)
                    return token, index
                else:
                    raise SyntaxError("Invalid condition")
            else:
                index += 1
                token = tokens[index]
                if token.type == 'identifier'or token.type=='numeral':
                    print("Parsing expression condition2")
                    index = index +1
                    token = tokens[index]
                    print(index, token)
                    return token, index
                else:
                    raise SyntaxError("Invalid condition")

        elif token.type == 'eq' or token.type == 'noteq':
            index = index +1
            token = tokens[index]
            
            if token.type == 'identifier'or token.type=='numeral':
                print("Parsing expression condition2")
                index = index +1
                token = tokens[index]
                print(index, token)
                return token, index
            else:
                raise SyntaxError("Invalid condition")
        else:
            raise SyntaxError("Invalid condition")
    else:
       raise SyntaxError("Invalid condition")


#Parse a for loop
def parse_for_loop(tokens,index):
    print("Parsing for loop")
    token = tokens[index]
    print(index, token)
    if token.type == 'for':
        index +=1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'in':
                index +=1
                token =tokens[index]
                print(index, token)
                if token.type == 'range':
                    index +=1
                    token = tokens[index]
                    print(index, token)
                    if token.type == 'lparen':
                        index +=1
                        token = tokens[index]
                        
                        print(index, token)
                        if token.type == 'identifier' or token.type=='numeral':
                            index +=1
                            token = tokens[index]
                            print(index, token)
                            if token.type == 'comma':
                                index =index + 1
                                token = tokens[index]
                                print(index, token)
                                if token.type == 'identifier' or token.type=='numeral':
                                    index +=1
                                    token = tokens[index]
                                    print(index, token)
                                    if token.type=='rparen':
                                        index +=1
                                        token = tokens[index]
                                        print(index, token)
                                        if token.type=='colon':
                                            index +=1
                                            token = tokens[index]
                                            token , index = parse_body(tokens, index)
                                            print(index, token)
                                            print("Parsing body")
                                            if token.type=='newline':
                                                index +=1
                                                token = tokens[index]
                                                print(index, token)
                                                while tokens[index].type == 'newline':
                                                    index += 1
                                                    token = tokens[index]
                                                #token , index = parse_body(tokens, index)
                                            else:
                                                raise SyntaxError("Invalid for loop")
                                        else:
                                            raise SyntaxError("Invalid for loop")
                                    else:
                                        raise SyntaxError("Invalid for loop")
                                else:
                                    raise SyntaxError("Invalid for loop")
                            else:
                                    raise SyntaxError("Invalid for loop")
                        else:
                            raise SyntaxError("Invalid for loop")
                    else:
                            raise  SyntaxError("Invalid for loop")
                else:
                    raise SyntaxError("Invalid for loop")
            else:
                raise SyntaxError("Invalid for loop")
        else:
            raise SyntaxError("Invalid for loop")
    else:
        raise SyntaxError("Invalid for loop")
                    

def parse_print_statement(tokens, index):
    print("Parsing print statement")
    token = tokens[index]
    print(index, token)
    if token.type == 'print':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'lparen':
            index += 1
            token = tokens[index]
            print(index, token)

            # Parse the first expression
            if token.type == 'double quote':
                index += 1
                token = tokens[index]
                print(index, token)
                print("Found string:", token.value)
                if token.type== 'string_literal':
                    index += 1
                    token = tokens[index]
                    print(index, token)
            elif token.type == 'identifier':
                print("Found identifier:", token.value)
                index += 1
                token = tokens[index]
            elif token.type == 'numeral':
                print("Found numeral:", token.value)
                index += 1
                token = tokens[index]
            else:
                raise SyntaxError("Invalid print statement")


            # Parse additional expressions if any
            while token.type == 'comma':
                index += 1
                token = tokens[index]
                

                if token.type == 'double quote':
                    index += 1
                    token = tokens[index]
                    print("Found string:", token.value)
                    if token.type== 'string_literal':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                elif token.type == 'identifier':
                    print("Found identifier:", token.value)
                    index += 1
                    token = tokens[index]
                elif token.type == 'numeral':
                    print("Found numeral:", token.value)
                    index += 1
                    token = tokens[index]
                else:
                    raise SyntaxError("Invalid print statement")

            print(index, token)
            if token.type == 'rparen':
                index +=1
                token = tokens[index]
                token , index = parse_body(tokens, index)
                print(index, token)
                print("Parsing body")
                if token.type=='newline':
                        index +=1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]
                print("Print statement parsed successfully")
                
            else:
                raise SyntaxError("Invalid print statement")
        else:
            raise SyntaxError("Invalid print statement")
    else:
        raise SyntaxError("Invalid print statement")


def parse_inc_dec_statement(tokens, index):
    token = tokens[index]
    print(index, token)
    if token.type== 'inc' or 'dec':
        index +=1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier':
            index +=1
            token = tokens[index]
            print(index, token)
            if token.type == 'colon':
                index +=1
                token = tokens[index]
                if token.type == 'newline':
                    index +=1
                    token = tokens[index]
                    print(index, token)
                    while tokens[index].type == 'newline':
                        index += 1
                        token = tokens[index]
                print("Increment/Decrement statement parsed successfully")
                
            else:
                raise SyntaxError("Invalid increment/decrement statement")
        else:
            raise SyntaxError("Invalid increment/decrement statement")


def parse_input_statement(tokens, index):
    print("Parsing input statement")

    
    token = tokens[index]
    print(index, token)

    if token.type == 'int' :
        
                index += 1
                token = tokens[index]
                print(index, token)


                if token.type == 'lparen':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        
                        if token.type == 'input':
                            index += 1
                            token = tokens[index]
                            if token.type == 'lparen':
                                index += 1
                                token = tokens[index]

                                if token.type == 'double quote':
                                    print("Prompt:", token.value)
                                    index += 1
                                    token = tokens[index]
                                
                                    if token.type == 'string_literal':
                                        print("Prompt:", token.value)
                                        index += 1
                                        token = tokens[index] 
                                        
                                        if token.type == 'rparen':
                                            index +=1
                                            token = tokens[index]

                                            if token.type == 'rparen':
                                                index +=1
                                                token = tokens[index]
                                                token , index = parse_body(tokens, index)
                                                print(index, token)
                                                print("Parsing body")
                                                if token.type=='newline':
                                                        index +=1
                                                        token = tokens[index]
                                                        print(index, token)
                                                        while tokens[index].type == 'newline':
                                                            index += 1
                                                            token = tokens[index]
                                                    
                                                print("Input statement parsed successfully")

    elif token.type == 'input':
        
                            index += 1
                            token = tokens[index]
                            print (index, token)
                            if token.type == 'lparen':
                                index += 1
                                token = tokens[index]
                                print(index, token)

                                if token.type == 'double quote':
                                    print("Prompt:", token.value)
                                    index += 1
                                    token = tokens[index]
                                    print(index, token)
                                    
                                    if token.type == 'string_literal':
                                        print("Prompt:", token.value)
                                        index += 1
                                        token = tokens[index] 

                                        if token.type == 'rparen':
                                            print(index, token)
                                            index +=1
                                            token = tokens[index]
                                            token , index = parse_body(tokens, index)
                                            print(index, token)
                                            print("Parsing body")
                                            if token.type=='newline':
                                                    index +=1
                                                    token = tokens[index]
                                                    print(index, token)
                                                    while tokens[index].type == 'newline':
                                                        index += 1
                                                        token = tokens[index]
                                            print("Input statement parsed successfully")
                                        else:
                                            raise SyntaxError("Invalid input statement")
                                    else:
                                        raise SyntaxError("Invalid input statement")
                                else:
                                    raise SyntaxError("Invalid input statement")
                            else:
                                    raise SyntaxError("Invalid input statement")
    else:
        raise SyntaxError("Invalid input statement")
                    

def parse_expression(tokens, index):
    print("Parsing inside expression")
    token = tokens[index]
    print(index, token, 2)
    if token.type == 'assignment_operator':
        index += 1
        token = tokens[index]
        print(index, token )
        if token.type == 'identifier' or token.type == 'int' or token.type == 'float' or token.type == 'numeral' or token.type == 'flt_numeral' or token.type == 'double quote' or token.type == 'input':
            print("Parsing identifier expression")
            if token.type == 'input' or token.type == 'int' or token.type == 'float':
                print("helo")
                token, index = parse_input_statement(tokens, index)
            elif token.type == 'double quote':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'string_literal':
                    print(index, token)
                    index +=1
                    token = tokens[index]
                    token , index = parse_body(tokens, index)
                    print(index, token)
                    print("Parsing body")
                    if token.type=='newline':
                            index +=1
                            token = tokens[index]
                            print(index, token)
                            while tokens[index].type == 'newline':
                                index += 1
                                token = tokens[index]
                    print("parsed")
                    return {'type': 'string_literal_expression', 'value': token.value}, index  # Return expression and index
                else:
                    raise SyntaxError("Invalid string literal")
            elif token.type == 'numeral':
                print("numeral")
                index +=1
                token = tokens[index]
                token , index = parse_body(tokens, index)
                print(index, token)
                print("Parsing body")
                if token.type=='newline':
                        index +=1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]    
                print("parsed")
                return {'type': 'numeral_expression', 'value': token.value}, index  # Return expression and index
            elif token.type == 'flt_numeral':
                index +=1
                token = tokens[index]
                token , index = parse_body(tokens, index)
                print(index, token)
                print("Parsing body")
                if token.type=='newline':
                        index +=1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]   
                print("parsed")
                return {'type': 'flt_numeral_expression', 'value': token.value}, index  # Return expression and index
            elif token.type == 'identifier':
                index +=1
                token = tokens[index]
                token , index = parse_body(tokens, index)
                print(index, token)
                print("Parsing body")
                if token.type=='newline':
                        index +=1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]   
                print(index, token)
                print("parsed")
                return {'type': 'identifier_expression', 'identifier': token.value}, index  # Return expression and index
        else:
            raise SyntaxError("Invalid expression")
    else:
        # Handle error: Invalid expression
        raise SyntaxError("Invalid expression")
    
    
def parse_assignment_statement(tokens, index):
    print("Parsing assignment statement")

    token = tokens[index]
    print(index, token)
    if token.type == 'identifier':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'assignment_operator':
            print (index, token)
            token, index = parse_expression(tokens, index)
            return {'type': 'assignment_statement', 'expression': token}, index
        else:
            # Handle error: Invalid assignment statement
            raise SyntaxError("Expected '=' in assignment statement")
    else:
        # Handle error: Invalid assignment statement
        raise SyntaxError("Invalid variable name in assignment statement")


def parse_function(tokens, index):
    print("Parsing Function")
    token = tokens[index]
    print(index, token)
    if token.type == 'def':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'lparen':
                index += 1
                token = tokens[index]
                print(index, token)
                parameters = []
                if token.type != 'rparen':
                    # Parse the first parameter
                    if token.type == 'identifier' or token.type == 'numeral':
                        parameters.append(token.value)
                        index += 1
                        token = tokens[index]
                        print(index, token)
                    else:
                        raise SyntaxError("Invalid function")
                    
                    # Parse additional parameters if any
                    while token.type == 'comma':
                        print("Parsing additional parameters")
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        if token.type == 'identifier' or token.type == 'numeral':
                            parameters.append(token.value)
                            index += 1
                            token = tokens[index]
                            print(index, token)
                        else:
                            raise SyntaxError("Invalid function")
                    
                if token.type == 'rparen':
                    index += 1
                    token = tokens[index]
                    print(index, token)
                    if token.type == 'colon':
                        index += 1
                        token = tokens[index]
                        token, index = parse_body(tokens, index)
                        print(index, token)
                        print("Parsing body")
                        if token.type == 'newline':
                            index += 1
                            token = tokens[index]
                            print(index, token)
                            while token.type == 'newline':
                                index += 1
                                token = tokens[index]
                else:
                    raise SyntaxError("Invalid function")
            else:
                raise SyntaxError("Invalid function")
        else:
            raise SyntaxError("Invalid function")
    else:
        raise SyntaxError("Invalid function")


def parse_return_statement(tokens, index):
    token = tokens[index]
    print  (index, token)
    if token.type == 'return':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type != 'newline':
            if token.type ==  'identifier' or token.type == 'numeral' or token.type == 'flt_numeral' :
                index += 1
                token = tokens[index]
                if token.type == 'newline':
                    index += 1
                    token = tokens[index]
                    token, index = parse_body(tokens, index)
                    print(index, token)
                    print("Parsing body")
                    if token.type == 'newline':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        while token.type == 'newline':
                            index += 1
                            token = tokens[index]
            elif token.type == 'add' or token.type =='sub' or token.type =='mul' or token.type == 'div' or token.type =='mod':
                token, index = parse_operators_exp(tokens, index)
                print(index, token)
                if token.type == 'newline':
                    index += 1
                    token = tokens[index]
                    token, index = parse_body(tokens, index)
                    
                    print(index, token)
                    print("Parsing body")
                    if token.type == 'newline':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        while token.type == 'newline':
                            index += 1
                            token = tokens[index]
            else:
                raise SyntaxError("Invalid return statement: Expected newline after expressions")
        else:
            expressions = []
            index += 1
        return token, index
    return None, index


def parse_operators(tokens, index):
    print("Parsing Operators")
    token = tokens[index]
    print(index, token)
    if token.type == 'add' or token.type == 'sub' or token.type == 'mul' or token.type == 'div' or token.type == 'mod':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier' or token.type == 'numeral':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'comma':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'identifier' or token.type == 'number':
                    index += 1
                    token = tokens[index]
                    if token.type == 'newline':
                        index += 1
                        token = tokens[index]
                        token, index = parse_body(tokens, index)
                        print(index, token)
                        print("Parsing body")
                        if token.type == 'newline':
                            index += 1
                            token = tokens[index]
                            print(index, token)
                            while token.type == 'newline':
                                index += 1
                                token = tokens[index]
                                
                        return token, index
                    return token, index

    else: 
        raise SyntaxError("Invalid operator")


def parse_operators_exp(tokens, index):
    token = tokens[index]
    print(index, token)
    if token.type == 'add' or token.type == 'sub' or token.type == 'mul' or token.type == 'div' or token.type == 'mod':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier' or token.type == 'numeral':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'comma':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'identifier' or token.type == 'number':
                    index += 1
                    token = tokens[index]
                return token, index
            raise SyntaxError("Invalid operator")
        raise SyntaxError("Invalid operator")
    raise SyntaxError("Invalid operator")
 

def parse_function_call(tokens, index):
    print("Parsing Function call")
    token = tokens[index]
    print(index, token)
    if token.type == 'function_call':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'lparen':
                index += 1
                token = tokens[index]
                print(index, token)
                parameters = []
                if token.type != 'rparen':
                    # Parse the first parameter
                    if token.type == 'identifier' or token.type == 'numeral':
                        parameters.append(token.value)
                        index += 1
                        token = tokens[index]
                        print(index, token)
                    else:
                        raise SyntaxError("Invalid function")
                    
                    # Parse additional parameters if any
                    while token.type == 'comma':
                        print("Parsing additional parameters")
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        if token.type == 'identifier' or token.type == 'numeral':
                            parameters.append(token.value)
                            index += 1
                            token = tokens[index]
                            print(index, token)
                        else:
                            raise SyntaxError("Invalid function")
                    
                if token.type == 'rparen':
                    index += 1
                    token = tokens[index]
                    print(index, token)
                    if token.type == 'colon':
                        index += 1
                        token = tokens[index]
                        token, index = parse_body(tokens, index)
                        print(index, token)
                        print("Parsing body")
                        if token.type == 'newline':
                            index += 1
                            token = tokens[index]
                            print(index, token)
                            while token.type == 'newline':
                                index += 1
                                token = tokens[index]
                else:
                    raise SyntaxError("Invalid function")
            else:
                raise SyntaxError("Invalid function")
        else:
            raise SyntaxError("Invalid function")
    else:
        raise SyntaxError("Invalid function")

    
def parse_class_statement(tokens, index):
    print("Parsing class")
    token = tokens[index]
    print(index, token)
    if token.type == 'class':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'identifier':
            index += 1
            token = tokens[index]
            print(index, token)

            if token.type == 'colon':
                index += 1
                token = tokens[index]
                if token.type == 'def':
                    token, index = class_body(tokens, index)
                elif token.type == 'self':
                    token, index = class_body_values(tokens, index)
                token, index = parse_body(tokens, index)
                print(index, token)
                print("Parsing body")

                if token.type == 'newline':
                    index += 1
                    token = tokens[index]
                    print(index, token)
                    while tokens[index].type == 'newline':
                        index += 1
                        token = tokens[index]
                        print("class body")
                    # token , index = parse_body(tokens, index)
                else:
                    raise SyntaxError("Invalid class syntax")
            else:
                raise SyntaxError("Invalid class syntax")
        else:
            raise SyntaxError("Invalid class syntax")
    else:
        # Handle error: Invalid while loop
        raise SyntaxError("Invalid class syntax")

# Class body


def class_body(tokens, index):
    print("Parsing class body")
    token = tokens[index]
    print(index, token)
    if token.type == 'def':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == '__init__':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'lparen':
                index += 1
                token = tokens[index]
                print(index, token)
                parameters = []
                if token.type != 'rparen':
                    # Parse the first parameter
                    if token.type == 'identifier' or token.type == 'self'   or token.type == 'numeral':
                        parameters.append(token.value)
                        index += 1
                        token = tokens[index]
                        print(index, token)
                    else:
                        raise SyntaxError("Invalid function")
                    
                    # Parse additional parameters if any
                    while token.type == 'comma':
                        print("Parsing additional parameters")
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        if token.type == 'identifier' or token.type == 'numeral':
                            parameters.append(token.value)
                            index += 1
                            token = tokens[index]
                            print(index, token)
                        else:
                            raise SyntaxError("Invalid function")
                    
                if token.type == 'rparen':
                    index += 1
                    token = tokens[index]
                    print(index, token)
                    if token.type == 'colon':
                        print("match")
                        index += 1
                        token = tokens[index]
                        print(index, token, 2)
                        token, index = parse_body(tokens, index)
                        
                        if token.type == 'newline':
                            index += 1
                            token = tokens[index]
                            print(index, token)
                            while token.type == 'newline':
                                index += 1
                                token = tokens[index]
                else:
                    raise SyntaxError("Invalid function")
            else:
                raise SyntaxError("Invalid function")
        else:
            raise SyntaxError("Invalid function")
    else:
        raise SyntaxError("Invalid function")

# Class self assignment

def class_body_values(tokens, index):
    token = tokens[index]
    print("indie")
    print(index, token)
    if token.type == 'self':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'dot':
            index += 1
            token = tokens[index]
            print(index, token)
            if token.type == 'identifier':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'assignment_operator':
                    index += 1
                    token = tokens[index]
                    print(index, token)
                    if token.type == 'identifier':
                        index += 1
                        token = tokens[index]
                        token, index = parse_body(tokens, index)
                        print(index, token)
                        print("Parsing body")
                        if token.type == 'newline':
                            index += 1
                            token = tokens[index]
                            print(index, token)
                            while tokens[index].type == 'newline':
                                index += 1
                                token = tokens[index]
                                print("class body")
                            # token , index = parse_body(tokens, index)
                        else:
                            raise SyntaxError("Invalid class syntax")
                    else:
                        raise SyntaxError("Invalid class syntax")
                else:
                    raise SyntaxError("Invalid class syntax")
            else:
                raise SyntaxError("Invalid class syntax")
        else:
            raise SyntaxError("Invalid class syntax")
    else:
        raise SyntaxError("Invalid class syntax")    
    
    
    
def parse_if_condition(tokens, index):
    print("Parsing if condition")
    token = tokens[index]
    print(index, token)
    if token.type == 'if':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'lparen':
            print("Parsing condition")
            index = index + 1
            token = tokens[index]
            token, index = parse_condition(tokens, index)

            print(index, token)

            if token.type == 'rparen':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'colon':
                    index += 1
                    token = tokens[index]
                    token, index = parse_body(tokens, index)
                    print(index, token)
                    print("Parsing body")
                    if token.type == 'newline':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]
                    else:
                        raise SyntaxError("Invalid if condition")
                else:
                    raise SyntaxError("Expected : after parenthesis")
            else:
                raise SyntaxError("Expected ')' before colon")
        else:
            raise SyntaxError("Expected '(' after if condition")
    else:
        # Handle error: Invalid while loop
        raise SyntaxError("Invalid if loop")

# Parse an elif condition


def parse_elif_condition(tokens, index):
    print("Parsing if condition")
    token = tokens[index]
    print(index, token)
    if token.type == 'elif':
        index += 1
        token = tokens[index]
        print(index, token)
        if token.type == 'lparen':
            print("Parsing condition")
            index = index + 1
            token = tokens[index]
            token, index = parse_condition(tokens, index)

            print(index, token)

            if token.type == 'rparen':
                index += 1
                token = tokens[index]
                print(index, token)
                if token.type == 'colon':
                    index += 1
                    token = tokens[index]
                    token, index = parse_body(tokens, index)
                    print(index, token)
                    print("Parsing body")
                    if token.type == 'newline':
                        index += 1
                        token = tokens[index]
                        print(index, token)
                        while tokens[index].type == 'newline':
                            index += 1
                            token = tokens[index]
                    else:
                        raise SyntaxError("Invalid elif condition")
                else:
                    raise SyntaxError("Expected : after parenthesis")
            else:
                raise SyntaxError("Expected ')' before colon")
        else:
            raise SyntaxError("Expected '(' after elif condition")
    else:
        # Handle error: Invalid while loop
        raise SyntaxError("Invalid elif loop")

# Parse an else condition


def parse_else_condition(tokens, index):
    print("Parsing else condition")
    token = tokens[index]
    print(index, token)
    if token.type == 'else':
        print("Parsing condition")
        index = index + 1
        token = tokens[index]
        print(index, token)
        if token.type == 'colon':
            index += 1
            token = tokens[index]
            token, index = parse_body(tokens, index)
            print(index, token)
            print("Parsing body")
            if token.type == 'newline':
                index += 1
                token = tokens[index]
                print(index, token)
                while tokens[index].type == 'newline':
                    index += 1
                    token = tokens[index]
            else:
                raise SyntaxError("Invalid else condition")
        else:
            raise SyntaxError("Expected : after else")
    else:
        raise SyntaxError("Invalid else syntax")
 
 
 
 
def parse_object_call(tokens, index):
    token = tokens[index]
    if token.type == 'object_call':
        index += 1
        token = tokens[index]
        if token.type == 'identifier':
            object_name = token.value
            index += 1
            token = tokens[index]
            if token.type == 'assignment_operator':
                index += 1
                token = tokens[index]
                if token.type == 'identifier':
                    method_name = token.value
                    index += 1
                    token = tokens[index]
                    if token.type == 'lparen':
                        parameters = []
                        index += 1
                        token = tokens[index]
                        while token.type != 'rparen':
                            if token.type in ['identifier', 'numeral', 'flt_numeral','double quote']:
                                if token.type == 'double quote':
                                    index += 1
                                    token = tokens[index]
                                    if token.type == 'string_literal':
                                        parameters.append(token.value)
                                        
                                        
                                    else:
                                        raise SyntaxError("Invalid object call: Expected string literal")
                                parameters.append(token.value)
                            index += 1
                            token = tokens[index]
                            if token.type == 'comma':
                                index += 1
                                token = tokens[index]
                        index += 1
                        return {'type': 'object_call', 'object': object_name, 'method': method_name, 'parameters': parameters}, index
                    else:
                        raise SyntaxError("Invalid object call: Expected '(' after method name")
                else:
                    raise SyntaxError("Invalid object call: Expected method name")
            else:
                raise SyntaxError("Invalid object call: Expected assignment operator")
        else:
            raise SyntaxError("Invalid object call: Expected object name")
    else:
        raise SyntaxError("Invalid object call: Expected 'object_call' keyword")



                  
tokens = tokenize(code_input)

# Parse and execute the program
parse_program(tokens,index)





import ast

def tokenize_function_line(line_str):
    # 1. Parse the string into an AST tree
    # ast.parse returns a 'Module' node; we grab the first statement
    if line_str[0] == "#":
        return None
    expr_stmt = ast.parse(line_str.strip()).body[0]
    
    # 2. Ensure it's actually a function call
    if not isinstance(expr_stmt, ast.Expr) or not isinstance(expr_stmt.value, ast.Call):
        raise ValueError("Line is not a valid function call structure.")
        
    call_node = expr_stmt.value
    
    # 3. Extract the function name (the 'id' of the Name node)
    function_name = call_node.func.id
    
    # 4. Extract the arguments back into their raw string representations
    # ast.unparse() requires Python 3.9+
    arguments = [ast.unparse(arg).strip() for arg in call_node.args]
    
    return {
        "function": function_name,
        "arguments": arguments
    }

# --- Example Usage ---
lines = [
    "afcn(1, 2)",
    "bfcn(string_value, 3, 4)",
    "# This is a comment",
    "tri_add(3, 4, 5)"
]

for line in lines:
    tokens = tokenize_function_line(line)
    if tokens != None: 
        match tokens['function']:
            case 'tri_add':
                sum = 0
                for _ in tokens['arguments']:
                    sum += int(_)
                print (f"sum = {sum}")
            case _:
                print (tokens)

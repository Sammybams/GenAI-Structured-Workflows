"""
Function Calling with Azure OpenAI
- get_current_datetime: Returns current date/time in various formats
- calculate: Evaluates mathematical expressions
"""

import json
import math
from datetime import datetime
from typing import Any

import yaml

from client import client, deployment_name


# Load prompts from YAML
def load_prompts() -> dict:
    with open("prompts.yaml", "r") as f:
        return yaml.safe_load(f)


# ============ TOOL IMPLEMENTATIONS ============

def get_current_datetime(format: str = "datetime") -> str:
    """Get current date/time in the specified format."""
    now = datetime.now()
    
    formats = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.isoformat(),
        "day": now.strftime("%A"),
        "timestamp": str(int(now.timestamp()))
    }
    
    return formats.get(format, now.isoformat())


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Supports basic arithmetic and math module functions.
    """
    # Allowed names for safe evaluation
    allowed_names = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        # Math module functions
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "floor": math.floor,
        "ceil": math.ceil,
    }
    
    try:
        # Replace common math notations
        expr = expression.replace("^", "**")
        
        # Evaluate with restricted globals
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# Map function names to implementations
AVAILABLE_FUNCTIONS = {
    "get_current_datetime": get_current_datetime,
    "calculate": calculate,
}


# ============ OPENAI TOOLS SCHEMA ============

def get_tools_schema() -> list[dict]:
    """Generate OpenAI tools schema from YAML config."""
    prompts = load_prompts()
    tools = []
    
    for func_name, func_config in prompts["functions"].items():
        properties = {}
        required = []
        
        for param_name, param_config in func_config.get("parameters", {}).items():
            prop = {
                "type": param_config.get("type", "string"),
                "description": param_config.get("description", ""),
            }
            if "enum" in param_config:
                prop["enum"] = param_config["enum"]
            
            properties[param_name] = prop
            
            # If no default, it's required
            if "default" not in param_config:
                required.append(param_name)
        
        tools.append({
            "type": "function",
            "function": {
                "name": func_name,
                "description": func_config["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        })
    
    return tools


# ============ FUNCTION CALLING LOGIC ============

def execute_function_call(tool_call) -> str:
    """Execute a function call and return the result."""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    
    if func_name in AVAILABLE_FUNCTIONS:
        result = AVAILABLE_FUNCTIONS[func_name](**func_args)
        return result
    else:
        return f"Error: Unknown function '{func_name}'"


def chat_with_functions(user_message: str) -> str:
    """
    Send a message to Azure OpenAI with function calling capability.
    Handles the full conversation loop including function execution.
    """
    prompts = load_prompts()
    tools = get_tools_schema()
    
    messages = [
        {"role": "system", "content": prompts["system_prompt"]},
        {"role": "user", "content": user_message}
    ]
    
    # First API call - may return a function call
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"  # Let the model decide when to call functions
    )
    
    assistant_message = response.choices[0].message
    
    # Check if the model wants to call a function
    if assistant_message.tool_calls:
        # Add the assistant's message with tool calls
        messages.append(assistant_message)
        
        # Execute each function call
        for tool_call in assistant_message.tool_calls:
            result = execute_function_call(tool_call)
            
            # Add the function result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Second API call - get final response with function results
        final_response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            tools=tools,
        )
        
        return final_response.choices[0].message.content
    
    # No function call needed, return the direct response
    return assistant_message.content


# ============ DEMO / CLI ============

if __name__ == "__main__":
    print("=" * 50)
    print("Function Calling Demo with Azure OpenAI")
    print("=" * 50)
    
    test_queries = [
        "What time is it right now?",
        "What day of the week is it?",
        "What is 25 * 4 + 10?",
        "Calculate the square root of 144",
        "What is 2 to the power of 10?",
        "What's today's date and also calculate 15% of 200",
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        response = chat_with_functions(query)
        print(f"Assistant: {response}")
        print("-" * 40)

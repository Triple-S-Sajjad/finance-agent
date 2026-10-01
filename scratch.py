import sys
import json
import ollama
from finance_agent.tools.calculators import EMI_SCHEMA, calculate_emi, ToolArgError

SYSTEM = """You are a personal finance assistant.
- Never calculate numbers yourself. Use tools.
- Only state numbers that came from a tool result or the user.
- Use the currency given in the tool result. Never assume one.
- If a required input is missing, ask for it.
- Be brief. No closing pleasantries."""

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": sys.argv[1]}]

def chat():
    return ollama.chat(model="qwen3:8b", messages=messages, tools=[EMI_SCHEMA],
                       think=False, options={"temperature": 0})

# 1. Model decides whether to call the tool
resp = chat()
messages.append(resp.message)

if not resp.message.tool_calls:
    print("answer:", resp.message.content)
    sys.exit()

# 2. Your code runs the tool. Errors go back to the model as data, not crashes.
for call in resp.message.tool_calls:
    try:
        result = calculate_emi(call.function.arguments)
    except ToolArgError as e:
        result = {"error": str(e)}
    print("tool result:", result)
    messages.append({"role": "tool", "tool_name": call.function.name, "content": json.dumps(result)})

# 3. Model writes the answer using the tool's result
resp = chat()
print("answer:", resp.message.content)
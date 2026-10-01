import json
import ollama
from finance_agent.log import log_event
from finance_agent.tools import run_tool, schemas

MODEL = "qwen3:8b"
MAX_STEPS = 5

SYSTEM = """You are a personal finance assistant.
- Never calculate numbers yourself. Use tools.
- Only state numbers that came from a tool result or the user.
- Use the currency given in the tool result. Never assume one.
- If a required input is missing, ask for it.
- Be brief. No closing pleasantries."""


class Agent:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM}]

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        log_event("user", {"text": text})

        for _ in range(MAX_STEPS):
            resp = ollama.chat(model=MODEL, messages=self.messages, tools=schemas(),
                               think=False, options={"temperature": 0})
            msg = resp.message
            self.messages.append(msg)

            if not msg.tool_calls:
                log_event("answer", {"text": msg.content})
                return msg.content

            for call in msg.tool_calls:
                result = run_tool(call.function.name, call.function.arguments)
                log_event("tool_call", {"name": call.function.name,
                                        "args": call.function.arguments, "result": result})
                self.messages.append({"role": "tool", "tool_name": call.function.name,
                                      "content": json.dumps(result)})

        log_event("step_limit", {})
        return "Stopped: too many tool calls without an answer."
import json
from finance_agent.log import log_event
import ollama
from finance_agent.tools.calculators import EMI_SCHEMA, calculate_emi, ToolArgError

MODEL = "qwen3:8b"
MAX_STEPS = 5   # hard cap on model round-trips per question; prevents infinite loops

SYSTEM = """You are a personal finance assistant.
- Never calculate numbers yourself. Use tools.
- Only state numbers that came from a tool result or the user.
- Use the currency given in the tool result. Never assume one.
- If a required input is missing, ask for it.
- Be brief. No closing pleasantries."""

TOOLS = {"calculate_emi": calculate_emi}
SCHEMAS = [EMI_SCHEMA]


class Agent:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM}]  # persists across questions

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        log_event("user", {"text": text})

        for _ in range(MAX_STEPS):
            resp = ollama.chat(model=MODEL, messages=self.messages, tools=SCHEMAS,
                               think=False, options={"temperature": 0})
            msg = resp.message
            self.messages.append(msg)

            if not msg.tool_calls:          # no tool requested -> this is the final answer
                log_event("answer", {"text": msg.content})
                return msg.content

            for call in msg.tool_calls:     # run each requested tool, feed results back
                result = self._run(call.function.name, call.function.arguments)
                log_event("tool_call", {"name":call.function.name, "args": call.function.arguments, "result": result})
                self.messages.append({"role": "tool", "tool_name": call.function.name,
                                      "content": json.dumps(result)})

        return "Stopped: too many tool calls without an answer."

    def _run(self, name: str, args: dict) -> dict:
        fn = TOOLS.get(name)
        if fn is None:                       # model invented a tool name
            return {"error": f"unknown tool '{name}'"}
        try:
            return fn(args)
        except ToolArgError as e:
            return {"error": str(e)}
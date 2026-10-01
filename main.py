from finance_agent.agent import Agent

agent = Agent()
print("Finance agent. Type 'exit' to quit.")
while True:
    text = input("\nyou> ").strip()
    if text.lower() in {"exit", "quit"}:
        break
    if text:
        print("\nagent>", agent.ask(text))
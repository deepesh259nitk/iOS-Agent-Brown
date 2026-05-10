import json
from openai import OpenAI
from tools import TOOLS
from prompts import SYSTEM_PROMPT

client = OpenAI()

# Conversation memory (critical for agent context)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def call_llm():
    """
    Calls the model and forces structured JSON output.
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        response_format={"type": "json_object"}  # forces structured output
    )

    return response.choices[0].message.content


def run_agent(task: str):
    """
    Main autonomous loop
    """

    print(f"\n🚀 Starting task: {task}\n")

    messages.append({
        "role": "user",
        "content": task
    })

    iteration = 0
    MAX_ITERATIONS = 30  # safety limit to avoid infinite loops

    while iteration < MAX_ITERATIONS:

        iteration += 1

        print(f"\n--- Iteration {iteration} ---")

        # 1. Ask LLM for next action
        raw_output = call_llm()

        print("LLM OUTPUT:", raw_output)

        try:
            action = json.loads(raw_output)
        except Exception as e:
            print("❌ Invalid JSON from model:", e)

            messages.append({
                "role": "user",
                "content": "Invalid JSON. Return ONLY valid JSON."
            })
            continue

        # 2. Check if task is complete
        if action.get("action") == "finish":
            print("\n🎉 Task completed by agent")
            break

        # 3. Extract tool call
        tool_name = action.get("action")
        args = action.get("args", {})

        if tool_name not in TOOLS:
            print(f"❌ Unknown tool: {tool_name}")

            messages.append({
                "role": "user",
                "content": f"Unknown tool: {tool_name}. Use only valid tools."
            })
            continue

        # 4. Execute tool
        print(f"🛠 Running tool: {tool_name} | args: {args}")

        try:
            result = TOOLS[tool_name](**args)
        except Exception as e:
            result = f"Tool execution error: {str(e)}"

        print("🔄 TOOL RESULT:\n", result)

        # 5. Feed result back to LLM (this creates the “loop”)
        messages.append({
            "role": "assistant",
            "content": raw_output
        })

        messages.append({
            "role": "user",
            "content": f"Tool result:\n{result}"
        })

    print("\n🛑 Agent stopped")


# Entry point
if __name__ == "__main__":
    task = input("Enter task for iOS agent: ")
    run_agent(task)
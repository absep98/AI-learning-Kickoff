import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "day-27" / "awesome-project"))
from assistant import groq_client
import json
MODEL = "qwen/qwen3.8-27b"
days_dir = Path(__file__).parent.parent.parent / "days"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_day_note",
            "description": "Read the learning note for one specific day number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer", "description": "The day number, e.g. 42"}
                },
                "required": ["day"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

response = groq_client.chat.completions.create(
    model=MODEL,
    temperature=0,
    messages=[{"role": "user", "content": "what did I learn on day 42?, and what time is it?"}],
    tools=TOOLS,
)

def read_day_note(day):
    days = list(days_dir.glob(f"day-{day:02d}-*.md"))
    if not days:
        return "No note for that day"
    return days[0].read_text(encoding="utf-8")

calls = response.choices[0].message.tool_calls
print(len(calls))
for c in calls:
    print(c.function.name, c.function.arguments)
call = response.choices[0].message.tool_calls[0]
day = json.loads(call.function.arguments)["day"]
note = read_day_note(day)
messages = [
    {"role": "user", "content": f"what did i learn on day {day}?, and what time is it"},
    response.choices[0].message,
    {"role": "tool", "tool_call_id": call.id, "content": note},
]

second = groq_client.chat.completions.create(
    model=MODEL,
    temperature=0,
    messages=messages,
    tools=TOOLS,
)

print(second.choices[0].message.content)
print(second.choices[0].message.tool_calls)


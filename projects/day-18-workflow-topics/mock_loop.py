from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


MAX_STEPS = 8
RETRY_COUNT = 3
ONE_SHOT_MODE = False
USE_REAL_MODEL_PLANNER = True
USE_REAL_TOOL_EXECUTOR = True
ALLOWED_ACTIONS = {"read_progress_files", "summarize_status", "ask_clarification"}

load_dotenv(r"C:\learning\aithings\.env")
api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=api_key) if api_key else None
REPO_ROOT = Path(r"C:\learning\aithings")

@dataclass
class StepLog: 
    step: int
    intent: str
    action: str
    result: str
    next_decision: str

def plan_action(intent):
    intent = intent.lower()
    
    if "progress" in intent or "roadmap" in intent:
        return "read_progress_files"

    if "summarize" in intent or "status" in intent:
        return "summarize_status"
    else:
        return "ask_clarification"

def mock_tool_call(action, intent, attempt_number):
    if "failonce" in intent and attempt_number == 1:
        return {"ok": "false", "message": "temporary timeout"}

    if action == "read_progress_files":
        return {"ok": "true", "message": "Read progress.md and roadmap.md"}
    
    if action == "summarize_status":
        return {"ok": "true", "message": "Prepared completed/pending summary"}
    
    return {"ok": "true", "message": "Need more details from user"}


def real_tool_call(action):
    if action == "read_progress_files":
        progress_path = REPO_ROOT / "progress.md"
        roadmap_path = REPO_ROOT / "roadmap.md"
        try:
            progress_text = progress_path.read_text(encoding="utf-8")
            roadmap_text = roadmap_path.read_text(encoding="utf-8")
            return {
                "ok": "true",
                "message": (
                    f"Read progress.md ({len(progress_text)} chars) and "
                    f"roadmap.md ({len(roadmap_text)} chars)"
                ),
            }
        except OSError as err:
            return {"ok": "false", "message": f"file read error: {err}"}

    if action == "summarize_status":
        progress_path = REPO_ROOT / "progress.md"
        try:
            lines = progress_path.read_text(encoding="utf-8").splitlines()
            focus_line = next((ln for ln in lines if ln.startswith("**Current Day:**")), "**Current Day:** unknown")
            goal_line = next((ln for ln in lines if ln.startswith("**Main Goal:**")), "**Main Goal:** unknown")
            return {"ok": "true", "message": f"Status summary prepared: {focus_line} | {goal_line}"}
        except OSError as err:
            return {"ok": "false", "message": f"file read error: {err}"}

    return {"ok": "true", "message": "Need more details from user"}

def execute_with_retry(action, intent):
    response = {"ok": "false", "message": "no attempts made"}
    for attempt_number in range(1, RETRY_COUNT + 1):
        if "failonce" in intent and attempt_number == 1:
            response = {"ok": "false", "message": "temporary timeout"}
        elif USE_REAL_TOOL_EXECUTOR:
            response = real_tool_call(action)
        else:
            response = mock_tool_call(action, intent, attempt_number)

        if response.get("ok") == "true":
            return response

    return response
        
def model_plan_action(intent, context):
    if not groq_client:
        return plan_action(intent)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an action planner. Return ONLY one action string from this set: "
                        "read_progress_files, summarize_status, ask_clarification. "
                        "No JSON, no explanation."
                    ),
                },
                {"role": "user", "content": f"Intent: {intent}\nContext: {context}\n"}
            ]
        )

        action = response.choices[0].message.content.strip().lower()
        action = action.replace("`", "").replace('"', "").replace("'", "")
        action = action.splitlines()[0].strip()

        if action in ALLOWED_ACTIONS:
            return action

        return plan_action(intent)
    except Exception:
        return plan_action(intent)

def run_mock_loop():
    logs = []
    completed_actions = []

    stop_reason = 'step limit reached'

    for i in range(1, MAX_STEPS+1):
       
        prompt = input(f"Step {i} > ")
        prompt = prompt.strip()
        if prompt == "":
            log = StepLog(
                step= i,
                intent= prompt,
                action= "none",
                result= "missing input",
                next_decision= "stop",
            )
            logs.append(log)
            stop_reason = "missing input"
            break

        if prompt.lower() in ["quit", "exit"]:
            log = StepLog(
                step= i,
                intent= prompt,
                action= "none",
                result= "user quit",
                next_decision= "stop",
            )
            logs.append(log)
            stop_reason = "user quit"
            break

        previous_action = logs[-1].action if logs else "none"
        context = (
            f"step={i}; previous_action={previous_action}; "
            f"allowed_actions={', '.join(sorted(ALLOWED_ACTIONS))}"
        )

        if USE_REAL_MODEL_PLANNER:
            action = model_plan_action(prompt, context)
        else:
            action = plan_action(prompt)

        if action not in ALLOWED_ACTIONS:
            action = "ask_clarification"

        response = execute_with_retry(action, prompt)

        if action != "ask_clarification" and response.get("ok") == "true":
            completed_actions.append(action)
            if ONE_SHOT_MODE:
                next_decision = "respond_and_stop"
                stop_reason = "success"
            else:
                next_decision = "continue"
        else:
            next_decision = "continue"

        log = StepLog(
            step=i,
            intent=prompt,
            action=action,
            result=response.get("message", "no message"),
            next_decision=next_decision,
        )
        logs.append(log)

        if next_decision == "respond_and_stop":
            break

    pending_items = [
        "connect real model",
        "connect real tools",
        "persist logs",
    ]

    print("\n=== Final Output Summary ===")
    print(f"Completed actions: {completed_actions if completed_actions else ['none']}")
    print(f"Pending items: {pending_items}")
    print(f"Stop reason: {stop_reason}")

    print("\n=== Step Logs ===")
    for log in logs:
        print(
            f"step={log.step} | intent={log.intent!r} | action={log.action} | "
            f"result={log.result} | next_decision={log.next_decision}"
        )

if __name__ == "__main__":
    run_mock_loop()
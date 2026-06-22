from dataclasses import dataclass


MAX_STEPS = 8
RETRY_COUNT = 3
ONE_SHOT_MODE = False


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

def execute_with_retry(action, intent):
    response = {"ok": "false", "message": "no attempts made"}
    for attempt_number in range(1, RETRY_COUNT + 1):
        response = mock_tool_call(action, intent, attempt_number)
        if response.get("ok") == "true":
            return response

    return response
        

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

        action = plan_action(prompt)
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
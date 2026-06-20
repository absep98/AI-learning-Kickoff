import subprocess
import sys
import json
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv(r"C:\learning\aithings\.env")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_diff(mode):
    if mode == 'unstaged':
        result = subprocess.run(
            ["git", "-C", r"C:\learning\aithings", "diff"],
            capture_output=True,
            text=True,
            check=False
        )

        return result.stdout
    
    elif mode == 'staged':
        result = subprocess.run(
            ['git', '-C', r"C:\learning\aithings", 'diff', '--cached'],
            capture_output=True,
            text=True,
            check=False
        )
        
        return result.stdout
    
    elif mode == 'both':
        result1 = subprocess.run(
            ["git", "-C", r"C:\learning\aithings", "diff"],
            capture_output=True,
            text=True,
            check=False
        )

        result2 = subprocess.run(
            ['git', '-C', r"C:\learning\aithings", 'diff', '--cached'],
            capture_output=True,
            text=True,
            check=False
        )

        result = result1.stdout +  "\n--- STAGED ---\n" + result2.stdout
        return result
    
    return ""

def main(mode):

    if mode not in ['staged', 'unstaged', 'both']:
        print("Invalid mode. Use unstaged, staged or both")
        return

    diff_text = get_diff(mode)
    
    if not diff_text.strip():
        print("No changes found.")
        return

    report = summarize_diff(diff_text, mode)
    print("\n=== What Changed ===")
    print(report.get("summary", "No summary available."))

    print("\n=== Risky Changes ===")
    risks = report.get("risks", [])
    if risks:
        for risk in risks:
            print(f"- {risk}")
    else:
        print("- No major risks identified")

    print("\n=== Suggested Commit Message ===")
    print(report.get("commit_message", "chore: update code"))

def summarize_diff(diff_text, mode):
    # Keep payload small enough for reliable API calls.
    diff_for_model = diff_text[:12000]

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You analyze git diffs. Respond with ONLY valid JSON in this exact shape: "
                    "{\"summary\": \"...\", \"risks\": [\"...\"], \"commit_message\": \"...\"}. "
                    "Keep summary concise. Risks should be concrete and actionable."
                ),
            },
            {"role": "user", "content": f"Mode: {mode}\n Diff length: {len(diff_for_model)}\n Git Diff: \n{diff_text}\n"}
        ]
    )

    full_response = response.choices[0].message.content.strip()
    
    # strip markdown code fences if model wraps JSON in ```json ... ```
    if full_response.startswith("```"):
        full_response = full_response.split("```")[-2] if "```" in full_response else full_response
        full_response = full_response.lstrip("json").strip()
    
        # Extract just the JSON object if model added extra text after it
    start = full_response.find("{")
    end = full_response.rfind("}") + 1
    if start != -1 and end > start:
        full_response = full_response[start:end]
    
    try:
        parsed = json.loads(full_response)
        return {
            "summary": parsed.get("summary", ""),
            "risks": parsed.get("risks", []),
            "commit_message": parsed.get("commit_message", "")
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "summary": full_response,
            "risks": ["Model response was not valid JSON"],
            "commit_message": "chore: update code"
        }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else 'unstaged'
    main(mode)
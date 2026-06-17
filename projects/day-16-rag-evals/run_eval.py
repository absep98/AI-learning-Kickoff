"""
Day 16 - RAG Evaluation System
Test your RAG with automated question sets
"""

import json
import sys
import os
from pathlib import Path

# Add day-15 to path so we can import the RAG
sys.path.append(str(Path(__file__).parent.parent / "day-15-cloud-api"))

from rag_gemini import query_rag


def load_eval_questions(filepath="eval_questions.json"):
    """Load evaluation questions from JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def check_answer_match(answer, expected_answer):
    """
    Check if the answer contains expected concepts.
    Case-insensitive substring matching with normalization.
    """
    print(f"    [ANSWER CHECK]")
    print(f"      RAG answered : '{answer[:120]}'")
    print(f"      We expected  : '{expected_answer}'")

    # Step 1: Normalize - lowercase and unify dash types (en-dash – vs hyphen -)
    answer_norm = answer.lower().replace('–', '-').replace('—', '-')
    expected_norm = expected_answer.lower().replace('–', '-').replace('—', '-')
    print(f"      After normalize: answer='{answer_norm[:80]}' | expected='{expected_norm}'")

    # Step 2: Direct substring check — does the exact expected text appear in the answer?
    if expected_norm in answer_norm:
        print(f"      → Direct match found! ✓")
        return True

    # Step 3: Word overlap check — at least 60% of expected words must appear
    expected_words = expected_norm.split()
    matched_words = [w for w in expected_words if w in answer_norm]
    unmatched_words = [w for w in expected_words if w not in answer_norm]
    ratio = len(matched_words) / len(expected_words) if expected_words else 1.0
    print(f"      Matched words : {matched_words}")
    print(f"      Missing words : {unmatched_words}")
    print(f"      Word overlap  : {len(matched_words)}/{len(expected_words)} = {ratio:.0%} (need ≥60%)")

    result = ratio >= 0.6
    print(f"      → {'PASS ✓' if result else 'FAIL ✗'}")
    return result


def check_sources_match(sources, expected_sources):
    """
    Check if any expected source appears in retrieved sources.
    """
    print(f"    [SOURCE CHECK]")
    print(f"      Expected sources : {expected_sources}")
    print(f"      Retrieved sources: {sources}")

    if not expected_sources:
        print(f"      → No source requirement, auto-PASS ✓")
        return True

    # Check if any expected file appears anywhere in the retrieved sources list
    for expected_src in expected_sources:
        for actual_src in sources:
            if expected_src in actual_src:
                print(f"      → Found '{expected_src}' in retrieved sources! ✓")
                return True

    print(f"      → None of the expected sources were retrieved ✗")
    return False


def run_evaluation():
    """Run full evaluation suite"""
    print("=" * 70)
    print("RAG EVALUATION SYSTEM - Day 16")
    print("=" * 70)
    print()
    
    # Load questions
    questions = load_eval_questions()
    print(f"Loaded {len(questions)} evaluation questions\n")
    # Track results
    results = []
    passed = 0
    failed = 0
    
    # Run each question
    for item in questions:
        q_id = item["id"]
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_sources = item.get("expected_sources", [])

        print()
        print(f"{'─' * 70}")
        print(f"  Q{q_id}: {question}")
        print(f"{'─' * 70}")

        # STEP 1: Send question to RAG
        print(f"  [STEP 1] Sending question to RAG...")
        try:
            response = query_rag(question)
            answer = response.get("answer", "")
            confidence = response.get("confidence", "unknown")
            sources = response.get("sources", [])
            print(f"  [STEP 1] RAG responded. Confidence={confidence}")
            print(f"  [STEP 1] Sources retrieved: {sources}")

            # STEP 2: Check if answer matches expected
            print(f"  [STEP 2] Checking answer quality...")
            answer_match = check_answer_match(answer, expected_answer)

            # STEP 3: Check if correct sources were retrieved
            print(f"  [STEP 3] Checking source retrieval...")
            sources_match = check_sources_match(sources, expected_sources)

            # STEP 4: Final verdict
            test_passed = answer_match and sources_match
            if test_passed:
                passed += 1
                print(f"  [RESULT] ✓ PASS (answer={answer_match}, sources={sources_match})")
            else:
                failed += 1
                reasons = []
                if not answer_match: reasons.append("answer wrong")
                if not sources_match: reasons.append("wrong sources")
                print(f"  [RESULT] ✗ FAIL — {', '.join(reasons)}")

            print()
            
            results.append({
                "id": q_id,
                "question": question,
                "passed": test_passed,
                "answer_match": answer_match,
                "sources_match": sources_match,
                "answer": answer,
                "confidence": confidence,
                "sources": sources
            })
            
        except Exception as e:
            failed += 1
            print(f"  ✗ ERROR: {e}")
            print()
            results.append({
                "id": q_id,
                "question": question,
                "passed": False,
                "error": str(e)
            })
    
    # Print summary
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    total = len(questions)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Total Questions: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print()
    
    # Save results
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print("Detailed results saved to eval_results.json")
    
    return pass_rate >= 80  # Success if 80%+ pass


if __name__ == "__main__":
    success = run_evaluation()
    sys.exit(0 if success else 1)

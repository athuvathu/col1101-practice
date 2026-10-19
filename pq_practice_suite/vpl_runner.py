#!/usr/bin/env python3
"""
vpl_runner.py - Unified VPL CLI Test Runner & Grading Engine
COL1101 Diwali 2026 Programming Quiz Practice Suite

Usage:
    python3 vpl_runner.py test <exam1|exam2> <q1|q2> [student_code|solution]
    python3 vpl_runner.py grade <exam1|exam2|all> [student_code|solution]
    python3 vpl_runner.py reset <exam1|exam2> <q1|q2>
"""

import sys
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EXAMS = {
    "exam1": {
        "q1": BASE_DIR / "exam1" / "Q1_Trie_Frequency_Filter",
        "q2": BASE_DIR / "exam1" / "Q2_Augmented_Order_BST",
    },
    "exam2": {
        "q1": BASE_DIR / "exam2" / "Q1_Dual_Heap_Scheduler",
        "q2": BASE_DIR / "exam2" / "Q2_Cuckoo_Linear_Hash",
    }
}


def run_test(exam_name: str, q_name: str, target: str = "student_code") -> int:
    exam_name = exam_name.lower()
    q_name = q_name.lower()

    if exam_name not in EXAMS or q_name not in EXAMS[exam_name]:
        print(f"Error: Invalid exam or question: {exam_name} {q_name}")
        print("Available: exam1 (q1, q2), exam2 (q1, q2)")
        return 1

    q_dir = EXAMS[exam_name][q_name]
    cmd = [sys.executable, str(q_dir / "test_suite.py"), target]
    print(f"\n[VPL-RUNNER] Executing: {' '.join(cmd)} in {q_dir.name}\n")
    res = subprocess.run(cmd, cwd=str(q_dir))
    return res.returncode


def grade_exam(exam_name: str, target: str = "student_code") -> None:
    exam_name = exam_name.lower()
    if exam_name == "all":
        for e in ["exam1", "exam2"]:
            grade_exam(e, target)
        return

    if exam_name not in EXAMS:
        print(f"Error: Unknown exam '{exam_name}'. Choose 'exam1', 'exam2', or 'all'.")
        return

    print(f"\n========================================================")
    print(f"             COL1101 1.5-HR MOCK: {exam_name.upper()}")
    print(f"             Target Code: {target}")
    print(f"========================================================")

    for q_name in ["q1", "q2"]:
        run_test(exam_name, q_name, target)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1].lower()

    if action == "test":
        if len(sys.argv) < 4:
            print("Usage: python3 vpl_runner.py test <exam1|exam2> <q1|q2> [student_code|solution]")
            sys.exit(1)
        exam = sys.argv[2]
        q = sys.argv[3]
        target = sys.argv[4] if len(sys.argv) > 4 else "student_code"
        sys.exit(run_test(exam, q, target))

    elif action == "grade":
        target_exam = sys.argv[2] if len(sys.argv) > 2 else "all"
        target = sys.argv[3] if len(sys.argv) > 3 else "student_code"
        grade_exam(target_exam, target)

    else:
        print(f"Unknown action: {action}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

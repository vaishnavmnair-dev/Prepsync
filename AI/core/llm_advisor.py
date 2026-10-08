"""
AI Advisor & Interview Coach.
Generates strategic executive coaching, empathetic feedback, and daily placement micro-drills.
Includes resilient fallback heuristics so it runs out-of-the-box in offline/demo environments,
with optional LLM enrichment when API keys are available.
"""

import json
import os
from typing import Any, Dict, Optional
import requests

from core.models import CareerGoal, DailyPlanItem, EnergyLevel, FullAIPlanningContext


class LLMAdvisor:
    """
    AI Strategic Advisor and Interview Micro-Coach.
    """

    @classmethod
    def generate_coach_guidance(cls, context: FullAIPlanningContext) -> str:
        student = context.student
        goal = context.career_goal
        energy = context.today_availability.energy_level
        avail = context.today_availability.available_duration_minutes
        streak = context.recent_progress.current_streak_days

        # Check for Gemini API key if configured
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                prompt = (
                    f"You are Bandwidth AI, an empathetic yet sharp engineering placement mentor. "
                    f"Student: {student.full_name}, Semester {student.current_semester} {student.branch}. "
                    f"Target Career: {goal.role_title} at {goal.target_company_type.value}. "
                    f"Today's Energy: {energy.value}. Available Study Time: {avail} minutes. Current Streak: {streak} days. "
                    f"Give a punchy, 3-sentence high-impact advice on how they should conquer today's schedule without burning out."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                pass  # Fall back to deterministic heuristic

        # Robust Built-in Heuristic Coach
        if energy == EnergyLevel.LOW:
            return (
                f"Hey {student.full_name}! Today was cognitively demanding at college, so our primary rule is: "
                f"Zero Burnout. Finish your time-boxed academic submission early, and hit your 15-minute {goal.role_title} "
                f"micro-drill. Completing that preserves your {streak}-day streak and keeps you ahead of 80% of peers who completely drop prep during fatigue."
            )
        elif energy == EnergyLevel.HIGH:
            return (
                f"Energy is high today, {student.full_name}! Strike hard on your top skill gap while your mind is fresh. "
                f"Treat your college lab prep as a direct rehearsal for your upcoming {goal.role_title} interviews. "
                f"Maintain deep focus and lock in your {streak + 1}th streak day!"
            )
        else:
            return (
                f"Solid rhythm today, {student.full_name}. We have balanced your urgent college submissions "
                f"with a protected 35-minute placement block. Consistent daily micro-actions beat weekend cramming every single time. "
                f"Let's execute smoothly and extend your {streak}-day streak!"
            )

    @classmethod
    def generate_micro_drill(cls, skill_name: str, energy: EnergyLevel) -> Dict[str, Any]:
        """
        Generates a bite-sized, high-yield drill matching remaining energy.
        """
        drills = {
            "DSA": {
                EnergyLevel.LOW: {
                    "title": "Time Complexity Flash Drill: Two Pointers",
                    "estimated_minutes": 15,
                    "question": "Given a sorted array of N integers, how does the Two-Pointer approach find a pair with target sum in O(N) time and O(1) space compared to binary search O(N log N)?",
                    "hint_1": "Think about monotonicity: what happens when sum < target? Which pointer moves?",
                    "hint_2": "Left pointer only moves right, right pointer only moves left. Each element visited at most once.",
                    "interview_takeaway": "Standard warm-up round question for Amazon, Flipkart, and Atlassian.",
                    "sample_code": "int left = 0, right = n - 1;\nwhile(left < right) {\n    int sum = arr[left] + arr[right];\n    if (sum == target) return {left, right};\n    else if (sum < target) left++;\n    else right--;\n}"
                },
                EnergyLevel.MEDIUM: {
                    "title": "Infix to Postfix Stack Evaluation",
                    "estimated_minutes": 25,
                    "question": "Why do compilers convert Infix expressions to Postfix (Reverse Polish Notation) before evaluating them with an evaluation stack?",
                    "hint_1": "Infix expressions require operator precedence and parentheses parsing at runtime.",
                    "hint_2": "Postfix expressions have unambiguous evaluation order from left to right with no parentheses needed.",
                    "interview_takeaway": "Direct overlap with your Data Structures Lab submission and standard online assessment coding questions.",
                    "sample_code": "// Operands pushed to stack, operators pop 2 operands and push result"
                },
                EnergyLevel.HIGH: {
                    "title": "Subarray Sum Equals K (Prefix Sum + Hash Map)",
                    "estimated_minutes": 40,
                    "question": "Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k in O(N) time.",
                    "hint_1": "If current prefix_sum is S, check how many times (S - k) has appeared in the frequency hash map.",
                    "hint_2": "Initialize map with prefix_sum 0 having frequency 1 before looping.",
                    "interview_takeaway": "Top 50 LeetCode question asked by Google, Microsoft, and Uber.",
                    "sample_code": "unordered_map<int, int> mp; mp[0] = 1;\nint prefix = 0, count = 0;\nfor(int num : nums) {\n    prefix += num;\n    if(mp.count(prefix - k)) count += mp[prefix - k];\n    mp[prefix]++;\n}"
                }
            },
            "Operating Systems": {
                EnergyLevel.LOW: {
                    "title": "OS Process vs Thread Quiz",
                    "estimated_minutes": 15,
                    "question": "Why is thread context-switching significantly faster than process context-switching?",
                    "hint_1": "Threads within the same process share virtual memory address space (page tables).",
                    "hint_2": "No need to flush CPU Translation Lookaside Buffer (TLB) when switching threads.",
                    "interview_takeaway": "Essential Core CS round question for Cisco, Qualcomm, and Goldman Sachs.",
                    "sample_code": None
                },
                EnergyLevel.MEDIUM: {
                    "title": "Round Robin CPU Scheduling Quantum Analysis",
                    "estimated_minutes": 25,
                    "question": "What happens if the time quantum in Round Robin CPU scheduling is set: 1) Too large? 2) Too small?",
                    "hint_1": "As quantum -> infinity, Round Robin degenerates into FCFS (First Come First Served).",
                    "hint_2": "As quantum -> 0, CPU spends most of its time doing context switches (thrashing).",
                    "interview_takeaway": "Direct overlap with Operating Systems midterm exams and SDE interview rounds.",
                    "sample_code": None
                },
                EnergyLevel.HIGH: {
                    "title": "Banker's Algorithm Safe State Detection",
                    "estimated_minutes": 35,
                    "question": "Explain how the Safety Algorithm in Banker's deadlock avoidance guarantees that granting a resource request will not lead to deadlock.",
                    "hint_1": "Work = Available, Finish[i] = false. Find process where Need_i <= Work.",
                    "hint_2": "Assume process finishes, free its Allocation back to Work: Work += Allocation_i.",
                    "interview_takeaway": "Classic gatekeeper question in OS system architecture rounds.",
                    "sample_code": None
                }
            }
        }

        skill_key = skill_name if skill_name in drills else "DSA"
        drill_for_skill = drills[skill_key]
        return drill_for_skill.get(energy, drill_for_skill[EnergyLevel.MEDIUM])

    @classmethod
    def generate_task_breakdown(
        cls,
        task_title: str,
        subject: str = "Academics",
        task_type: str = "medium",
        duration_minutes: int = 40
    ) -> Dict[str, Any]:
        """
        Intelligently deconstructs an academic or prep task into manageable 5-15 minute micro-steps
        with a tailored instant kickstart tip to overcome procrastination.
        """
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                prompt = (
                    f"You are an empathetic, tactical academic AI coach. "
                    f"Break down this college student study task: '{task_title}' (Subject: {subject}, Duration: {duration_minutes} mins, Type: {task_type}). "
                    f"Respond ONLY with valid JSON with keys: "
                    f"'kickstart': string (a concrete 1-minute friction-free starting action), "
                    f"'steps': list of 3 to 5 actionable sub-steps with approximate minutes in parentheses like '(10 mins)', "
                    f"'step_minutes': list of integers corresponding to the durations of each step summing to around {duration_minutes}."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=4)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text.startswith("```"):
                        text = text.split("```")[1]
                        if text.startswith("json"):
                            text = text[4:]
                    parsed = json.loads(text.strip())
                    if "kickstart" in parsed and "steps" in parsed:
                        return {
                            "kickstart": parsed["kickstart"],
                            "steps": parsed["steps"],
                            "step_minutes": parsed.get("step_minutes", [10, 15, 10, 5])
                        }
            except Exception:
                pass

        # Robust Heuristic Topic Decomposer
        combined = f"{task_title} {subject}".lower()

        if any(k in combined for k in ["pointer", "c++", "c ", "code", "program", "dsa", "algo", "python", "java", "tree", "sql", "bug", "compiler", "function"]):
            return {
                "kickstart": f"Open your code editor or IDE right now for '{task_title}'. Create the source file and write down the starter boilerplate.",
                "steps": [
                    "Clarify the input format and sketch test constraints on paper (5 mins)",
                    f"Write the core logic loop and primary function for '{task_title}' (15 mins)",
                    "Add boundary conditions, null/empty checks, and error handling (10 mins)",
                    "Compile and execute with 2 custom test inputs to verify output (5 mins)"
                ],
                "step_minutes": [5, 15, 10, 5]
            }

        if any(k in combined for k in ["record", "lab", "experiment", "physics", "chemistry", "circuit", "manual", "apparatus", "specimen"]):
            return {
                "kickstart": f"Lay out your record notebook, pens, and open the lab sheet PDF for '{task_title}'. Copy the experiment title first.",
                "steps": [
                    "Write down the Aim, Apparatus required, and governing formula (8 mins)",
                    "Neatly sketch the circuit or experimental apparatus schematic (10 mins)",
                    "Enter sample observation readings and compute the percentage error (10 mins)",
                    "Write the 2-sentence conclusion, sign off, and pack your file (5 mins)"
                ],
                "step_minutes": [8, 10, 10, 5]
            }

        if any(k in combined for k in ["slide", "read", "deck", "chapter", "skim", "revision", "ppt", "pdf"]):
            return {
                "kickstart": f"Open slide 1 right now for '{task_title}' and skim headings and bold text without taking notes.",
                "steps": [
                    "Skim the first 5 slides/pages and highlight 3 core concepts/definitions (6 mins)",
                    "Summarize key takeaways in 3 bullet points in your own words (8 mins)",
                    "Test yourself with 2 quick practice or interview questions (6 mins)"
                ],
                "step_minutes": [6, 8, 6]
            }

        if any(k in combined for k in ["math", "calculus", "integral", "derivative", "matrix", "numerical", "solve", "algebra"]):
            return {
                "kickstart": f"Open a fresh notebook page and write down the governing formula for '{task_title}'.",
                "steps": [
                    "Identify standard form, integration/derivative rules, and substitution terms (7 mins)",
                    "Solve the first problem step-by-step showing full algebraic derivations (15 mins)",
                    "Solve the remaining numericals and check boundary values (10 mins)",
                    "Verify arithmetic signs and box the final answer neatly (5 mins)"
                ],
                "step_minutes": [7, 15, 10, 5]
            }

        # Fallback by difficulty type
        if task_type.lower() == "hard":
            return {
                "kickstart": f"Open your workspace right now for '{task_title}'. Write down the goal to break the initial inertia.",
                "steps": [
                    f"Deconstruct '{task_title}' into 2 smaller sub-goals on paper (5 mins)",
                    "Work through the most difficult component while your energy is peak (15 mins)",
                    "Complete secondary requirements and double-check edge cases (10 mins)",
                    "Run final review and verify completion (5 mins)"
                ],
                "step_minutes": [5, 15, 10, 5]
            }
        elif task_type.lower() == "light":
            return {
                "kickstart": f"Open your reference material right now for '{task_title}' and skim the highlights.",
                "steps": [
                    "Quickly skim key points and highlight core concepts (6 mins)",
                    "Summarize main takeaways in 3 bullet points (8 mins)",
                    "Test your recall with 2 quick questions (6 mins)"
                ],
                "step_minutes": [6, 8, 6]
            }
        else:
            return {
                "kickstart": f"Lay out your notebook, pens, and open materials for '{task_title}'. Write the heading first.",
                "steps": [
                    f"Review requirements and outline structure for '{task_title}' (8 mins)",
                    "Draft the core solution or write the first half (12 mins)",
                    "Complete the remaining sections and verify all details (10 mins)",
                    "Proofread final output and organize materials (5 mins)"
                ],
                "step_minutes": [8, 12, 10, 5]
            }



"""
Academic-Placement Synergy & Overlap Detector.
Identifies hidden interview and placement value inside mandatory college coursework,
preventing duplicate study time and highlighting direct industry applications.
"""

import re
from typing import List
from core.models import AcademicPlacementSynergy, AcademicTask


# Semantic mapping rules connecting academic keywords to placement skills and interview angles
SYNERGY_RULES = [
    {
        "pattern": r"(pointer|dynamic memory|malloc|free|memory leak|valgrind)",
        "skill": "C/C++",
        "synergy_type": "Memory Management & Pointer Internals",
        "description": "Your college assignment on pointers directly tests low-level memory allocation, stack vs heap, and pointer arithmetic.",
        "interview_takeaway": "Product company interviews frequently ask: 'What happens in memory when malloc fails?' and 'How do you detect dangling pointers and memory leaks?'",
        "time_saved_minutes": 45
    },
    {
        "pattern": r"(stack|queue|infix|postfix|expression|linked list|reverse)",
        "skill": "DSA",
        "synergy_type": "Data Structures Application",
        "description": "Your lab submission implements stack and queue expressions, which is a classic LeetCode Medium problem pattern.",
        "interview_takeaway": "Pay special attention to operator precedence map and edge cases with unbalanced parentheses (frequent online assessment question).",
        "time_saved_minutes": 60
    },
    {
        "pattern": r"(tree|bst|binary search tree|traversal|inorder|level order)",
        "skill": "DSA",
        "synergy_type": "Tree Algorithms & Recursion",
        "description": "Tree traversals and binary search tree properties are the #1 most frequently tested data structure in SDE interviews.",
        "interview_takeaway": "Notice both recursive and iterative (using explicit stack) approaches for tree traversals.",
        "time_saved_minutes": 60
    },
    {
        "pattern": r"(cpu scheduling|round robin|priority scheduling|sjf|process|thread)",
        "skill": "Operating Systems",
        "synergy_type": "System Scheduling & Concurrency",
        "description": "Studying CPU scheduling for your college exam directly covers standard OS technical interview questions.",
        "interview_takeaway": "Interviewers will ask: 'Why does Round Robin suffer when quantum is too small (context switch thrashing)?' and 'How does multilevel feedback queue work?'",
        "time_saved_minutes": 90
    },
    {
        "pattern": r"(deadlock|banker|semaphore|mutex|critical section)",
        "skill": "Operating Systems",
        "synergy_type": "Synchronization & Concurrency",
        "description": "College concurrency theory translates 1:1 into system design and low-level engineering interview rounds.",
        "interview_takeaway": "Memorize the 4 Coffman conditions for deadlock and how Banker's algorithm detects safe state sequences.",
        "time_saved_minutes": 75
    },
    {
        "pattern": r"(sql|join|group by|having|normalization|bcnf|acid|transaction)",
        "skill": "DBMS",
        "synergy_type": "Database Queries & Design",
        "description": "Your DBMS assignment exercises relational schema design, 3NF/BCNF decomposition, and ACID guarantees.",
        "interview_takeaway": "Expect questions on isolation levels (Read Committed vs Serializable) and query optimization with B-Tree vs Hash indexing.",
        "time_saved_minutes": 60
    },
    {
        "pattern": r"(socket|tcp|udp|three-way handshake|http|dns|osi)",
        "skill": "Computer Networks",
        "synergy_type": "Networking Protocols",
        "description": "Socket programming and OSI layer homework directly prepares you for backend and infrastructure roles.",
        "interview_takeaway": "Be prepared to explain the exact packet lifecycle and TCP flags (SYN, SYN-ACK, ACK) during connection establishment.",
        "time_saved_minutes": 60
    },
    {
        "pattern": r"(oop|inheritance|polymorphism|virtual|interface|abstract)",
        "skill": "OOP",
        "synergy_type": "Object-Oriented Design Principles",
        "description": "Your lab exercises OOP concepts that interviewers evaluate during Low-Level Design (LLD) rounds.",
        "interview_takeaway": "Focus on runtime polymorphism via virtual tables (VTable) and how to design extensible code adhering to SOLID principles.",
        "time_saved_minutes": 45
    }
]


class SynergyDetector:
    """
    Detects semantic and conceptual overlaps between academic tasks and placement prep goals.
    """

    @classmethod
    def detect_synergies(cls, academic_tasks: List[AcademicTask]) -> List[AcademicPlacementSynergy]:
        synergies: List[AcademicPlacementSynergy] = []

        for task in academic_tasks:
            # Combine subject and title for regex inspection
            text_corpus = f"{task.subject} {task.task_title}".lower()

            for rule in SYNERGY_RULES:
                if re.search(rule["pattern"], text_corpus):
                    synergies.append(
                        AcademicPlacementSynergy(
                            academic_task_id=task.task_id,
                            academic_task_title=task.task_title,
                            academic_subject=task.subject,
                            relevant_placement_skill=rule["skill"],
                            synergy_type=rule["synergy_type"],
                            synergy_description=rule["description"],
                            recommended_interview_takeaway=rule["interview_takeaway"],
                            time_saved_minutes=rule["time_saved_minutes"]
                        )
                    )
                    break  # One primary synergy per academic task is sufficient

        return synergies


"""
Comprehensive taxonomy of engineering placement skills,
prerequisites, cognitive intensity ratings, and micro-prep drill templates.
"""

from typing import Dict, List, Any


SKILLS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "DSA": {
        "category": "DSA",
        "cognitive_intensity": "HIGH",  # Requires peak mental focus
        "prerequisites": ["C/C++", "Python"],
        "subtopics": [
            "Time & Space Complexity",
            "Arrays & Strings",
            "Linked Lists",
            "Stacks & Queues",
            "Recursion & Backtracking",
            "Binary Trees & BST",
            "Heaps & Priority Queues",
            "Hashing & HashMaps",
            "Graph Algorithms (BFS/DFS, Dijkstra)",
            "Dynamic Programming (1D, 2D)",
            "Greedy Algorithms"
        ],
        "micro_prep_tasks": [
            "Dry run 1 Two-Pointer Array question (15 min)",
            "Solve 1 String anagram / palindrome problem on LeetCode (20 min)",
            "Trace recursion tree for Subsets problem on pen & paper (15 min)",
            "Write Inorder/Preorder traversal iterative version (20 min)",
            "Review Top-K Frequent Elements using Min-Heap (15 min)"
        ]
    },
    "C/C++": {
        "category": "Programming",
        "cognitive_intensity": "MEDIUM",
        "prerequisites": [],
        "subtopics": [
            "Pointers & Memory Allocation",
            "Structures & Unions",
            "Pointers to Functions",
            "STL Vectors, Maps, Sets",
            "Pass by Reference vs Pointer",
            "Virtual Functions & VTable"
        ],
        "micro_prep_tasks": [
            "Trace pointer arithmetic snippet and identify dangling pointer (10 min)",
            "Implement a generic vector comparator using C++ STL (15 min)",
            "Explain differences between malloc and new in 5 bullet points (10 min)"
        ]
    },
    "DBMS": {
        "category": "Core CS",
        "cognitive_intensity": "MEDIUM",
        "prerequisites": [],
        "subtopics": [
            "Relational Model & Keys",
            "ER Diagrams",
            "Normalization (1NF to BCNF)",
            "Transactions & ACID Properties",
            "Concurrency Control & 2PL Locks",
            "Indexing (B-Trees vs Hash)",
            "Query Optimization"
        ],
        "micro_prep_tasks": [
            "Identify candidate keys and find highest normal form of a given schema (15 min)",
            "Explain the difference between Dirty Read and Non-Repeatable Read (10 min)",
            "Draft B-tree search order vs binary tree search order (12 min)"
        ]
    },
    "SQL": {
        "category": "Core CS",
        "cognitive_intensity": "MEDIUM",
        "prerequisites": ["DBMS"],
        "subtopics": [
            "GROUP BY and HAVING Clauses",
            "INNER, LEFT, RIGHT, FULL OUTER JOINS",
            "Correlated Subqueries",
            "Window Functions (ROW_NUMBER, DENSE_RANK)",
            "Aggregation with CASE WHEN",
            "Stored Procedures & Triggers"
        ],
        "micro_prep_tasks": [
            "Write query to find 2nd highest salary using DENSE_RANK() (15 min)",
            "Solve 1 HackerRank / LeetCode SQL 50 join question (15 min)",
            "Write a self-join query to find employee-manager hierarchies (12 min)"
        ]
    },
    "Operating Systems": {
        "category": "Core CS",
        "cognitive_intensity": "MEDIUM",
        "prerequisites": ["C/C++"],
        "subtopics": [
            "Process vs Thread & Context Switching",
            "CPU Scheduling Algorithms (SJF, Round Robin)",
            "Inter-Process Communication (Pipes, Shared Memory)",
            "Critical Section & Semaphores",
            "Deadlock Conditions & Banker's Algorithm",
            "Virtual Memory, Paging, Page Faults, LRU",
            "Disk Scheduling"
        ],
        "micro_prep_tasks": [
            "Calculate Average Turnaround Time for Round Robin with quantum = 2 (15 min)",
            "Explain 4 Coffman conditions for Deadlock with real-world analogy (10 min)",
            "Trace LRU page replacement algorithm for a 4-frame page reference string (12 min)"
        ]
    },
    "Computer Networks": {
        "category": "Core CS",
        "cognitive_intensity": "LOW_TO_MEDIUM",
        "prerequisites": [],
        "subtopics": [
            "OSI 7 Layers vs TCP/IP Model",
            "TCP 3-Way Handshake & Connection Teardown",
            "TCP vs UDP Trade-offs",
            "HTTP vs HTTPS (TLS/SSL Handshake)",
            "DNS Resolution Lifecycle",
            "Subnetting & CIDR Notation",
            "Routing Protocols (OSPF, BGP)"
        ],
        "micro_prep_tasks": [
            "Sketch TCP 3-way handshake with SYN/ACK flags and sequence numbers (10 min)",
            "Trace what happens when you type https://google.com in browser address bar (15 min)",
            "Solve a 24-bit subnet masking IP host calculation (10 min)"
        ]
    },
    "OOP": {
        "category": "Core CS",
        "cognitive_intensity": "LOW_TO_MEDIUM",
        "prerequisites": ["C/C++"],
        "subtopics": [
            "Encapsulation & Abstraction",
            "Inheritance & Diamond Problem",
            "Polymorphism (Compile-time vs Run-time)",
            "SOLID Principles",
            "Design Patterns (Singleton, Factory, Observer)"
        ],
        "micro_prep_tasks": [
            "Explain Virtual Function and VTable lookup in C++ (12 min)",
            "Refactor a code snippet violating the Open-Closed Principle (15 min)",
            "Write a thread-safe Singleton design pattern in code (15 min)"
        ]
    },
    "Web Development": {
        "category": "Development",
        "cognitive_intensity": "HIGH",
        "prerequisites": ["Git/GitHub"],
        "subtopics": [
            "Semantic HTML & Modern CSS Flexbox/Grid",
            "JavaScript ES6+, Promises, Async/Await, Event Loop",
            "React Components, State, Hooks (useState, useEffect)",
            "REST API Design & HTTP Status Codes",
            "JWT Authentication & Session Management",
            "Database ORM / ODM Connection"
        ],
        "micro_prep_tasks": [
            "Build an API call with async/await and robust error handling (15 min)",
            "Explain the JavaScript Event Loop (Microtask vs Macrotask queue) (12 min)",
            "Design a RESTful API schema for a student course registration system (15 min)"
        ]
    },
    "Git/GitHub": {
        "category": "Development",
        "cognitive_intensity": "LOW",
        "prerequisites": [],
        "subtopics": [
            "git init, add, commit, push, pull",
            "Branching & Merging (git branch, git checkout, git merge)",
            "Rebase vs Merge differences",
            "Resolving Merge Conflicts",
            "Writing Clean Conventional Commits & README"
        ],
        "micro_prep_tasks": [
            "Review git interactive rebase and cherry-pick syntax (10 min)",
            "Clean up commit history and write a professional GitHub repository README (15 min)"
        ]
    },
    "Aptitude": {
        "category": "Aptitude",
        "cognitive_intensity": "LOW_TO_MEDIUM",
        "prerequisites": [],
        "subtopics": [
            "Quantitative: Time & Work, Speed Distance Time, Percentages, Probability",
            "Logical: Syllogisms, Seating Arrangements, Blood Relations, Coding-Decoding",
            "Verbal: Sentence Correction, Reading Comprehension, Para Jumbles"
        ],
        "micro_prep_tasks": [
            "Solve 5 Time & Work questions with shortcut formulas (15 min)",
            "Solve 1 circular seating arrangement puzzle (15 min)",
            "Solve 5 probability ball-picking and dice questions (12 min)"
        ]
    },
    "Interview Preparation": {
        "category": "Interview",
        "cognitive_intensity": "LOW_TO_MEDIUM",
        "prerequisites": [],
        "subtopics": [
            "Resume Bullet Point Formatting (XYZ Formula: Accomplished [X] as measured by [Y], by doing [Z])",
            "Behavioral STAR Method (Situation, Task, Action, Result)",
            "Project Pitch in 90 seconds",
            "Mock Technical Coding Walkthrough",
            "Questions to Ask the Interviewer"
        ],
        "micro_prep_tasks": [
            "Draft 1 STAR method story for a challenging team conflict or deadline (15 min)",
            "Refactor 2 resume bullet points using the Google XYZ formula (15 min)",
            "Practice your 90-second 'Tell me about yourself' introduction out loud (10 min)"
        ]
    }
}


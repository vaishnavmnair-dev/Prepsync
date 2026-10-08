"""
Industry benchmark catalog for standard engineering placement roles.
Defines target proficiency (0-5), importance weights, and prerequisite order
across different company tiers (Product-based / Tier-1, Startups, Service-based).
"""

from typing import Dict, List, Any


ROLE_REQUIREMENTS: Dict[str, List[Dict[str, Any]]] = {
    "Software Developer": [
        {"skill_name": "DSA", "category": "DSA", "required_proficiency": 4, "importance": "Critical", "weight": 10.0, "recommended_order": 1},
        {"skill_name": "C/C++", "category": "Programming", "required_proficiency": 3, "importance": "High", "weight": 7.0, "recommended_order": 2},
        {"skill_name": "OOP", "category": "Core CS", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 3},
        {"skill_name": "DBMS", "category": "Core CS", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 4},
        {"skill_name": "SQL", "category": "Core CS", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 5},
        {"skill_name": "Operating Systems", "category": "Core CS", "required_proficiency": 3, "importance": "High", "weight": 8.0, "recommended_order": 6},
        {"skill_name": "Computer Networks", "category": "Core CS", "required_proficiency": 3, "importance": "Medium", "weight": 6.5, "recommended_order": 7},
        {"skill_name": "Web Development", "category": "Development", "required_proficiency": 3, "importance": "High", "weight": 7.5, "recommended_order": 8},
        {"skill_name": "Git/GitHub", "category": "Development", "required_proficiency": 3, "importance": "High", "weight": 7.0, "recommended_order": 9},
        {"skill_name": "Aptitude", "category": "Aptitude", "required_proficiency": 3, "importance": "High", "weight": 7.0, "recommended_order": 10},
        {"skill_name": "Interview Preparation", "category": "Interview", "required_proficiency": 4, "importance": "High", "weight": 8.5, "recommended_order": 11},
    ],
    "Backend Developer": [
        {"skill_name": "DSA", "category": "DSA", "required_proficiency": 4, "importance": "Critical", "weight": 9.5, "recommended_order": 1},
        {"skill_name": "Python", "category": "Programming", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 2},
        {"skill_name": "DBMS", "category": "Core CS", "required_proficiency": 5, "importance": "Critical", "weight": 10.0, "recommended_order": 3},
        {"skill_name": "SQL", "category": "Core CS", "required_proficiency": 5, "importance": "Critical", "weight": 10.0, "recommended_order": 4},
        {"skill_name": "Operating Systems", "category": "Core CS", "required_proficiency": 4, "importance": "High", "weight": 8.5, "recommended_order": 5},
        {"skill_name": "Computer Networks", "category": "Core CS", "required_proficiency": 4, "importance": "High", "weight": 8.5, "recommended_order": 6},
        {"skill_name": "Git/GitHub", "category": "Development", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 7},
        {"skill_name": "Interview Preparation", "category": "Interview", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 8},
    ],
    "Frontend Developer": [
        {"skill_name": "Web Development", "category": "Development", "required_proficiency": 5, "importance": "Critical", "weight": 10.0, "recommended_order": 1},
        {"skill_name": "DSA", "category": "DSA", "required_proficiency": 3, "importance": "High", "weight": 7.5, "recommended_order": 2},
        {"skill_name": "Git/GitHub", "category": "Development", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 3},
        {"skill_name": "Computer Networks", "category": "Core CS", "required_proficiency": 3, "importance": "Medium", "weight": 6.0, "recommended_order": 4},
        {"skill_name": "Aptitude", "category": "Aptitude", "required_proficiency": 3, "importance": "Medium", "weight": 6.5, "recommended_order": 5},
        {"skill_name": "Interview Preparation", "category": "Interview", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 6},
    ],
    "AI/ML Engineer": [
        {"skill_name": "Python", "category": "Programming", "required_proficiency": 5, "importance": "Critical", "weight": 10.0, "recommended_order": 1},
        {"skill_name": "DSA", "category": "DSA", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 2},
        {"skill_name": "SQL", "category": "Core CS", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 3},
        {"skill_name": "DBMS", "category": "Core CS", "required_proficiency": 3, "importance": "Medium", "weight": 7.0, "recommended_order": 4},
        {"skill_name": "Git/GitHub", "category": "Development", "required_proficiency": 3, "importance": "High", "weight": 7.5, "recommended_order": 5},
        {"skill_name": "Aptitude", "category": "Aptitude", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 6},
        {"skill_name": "Interview Preparation", "category": "Interview", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 7},
    ],
    "Data Analyst": [
        {"skill_name": "SQL", "category": "Core CS", "required_proficiency": 5, "importance": "Critical", "weight": 10.0, "recommended_order": 1},
        {"skill_name": "Python", "category": "Programming", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 2},
        {"skill_name": "DBMS", "category": "Core CS", "required_proficiency": 4, "importance": "High", "weight": 8.5, "recommended_order": 3},
        {"skill_name": "Aptitude", "category": "Aptitude", "required_proficiency": 4, "importance": "Critical", "weight": 9.0, "recommended_order": 4},
        {"skill_name": "Interview Preparation", "category": "Interview", "required_proficiency": 4, "importance": "High", "weight": 8.0, "recommended_order": 5},
    ]
}

# Modifiers based on company tier
TIER_PROFICIENCY_MODIFIERS: Dict[str, Dict[str, Any]] = {
    "FAANG / Tier-1": {
        "dsa_boost": 1,          # Expects advanced DSA (graphs, hard DP)
        "core_cs_boost": 1,      # Deep OS/Networks/System Design internals
        "urgency_multiplier": 1.25,
        "hours_per_proficiency_level": 40
    },
    "Product-based": {
        "dsa_boost": 0,          # Standard intermediate to advanced
        "core_cs_boost": 0,
        "urgency_multiplier": 1.1,
        "hours_per_proficiency_level": 30
    },
    "Unicorn Startup": {
        "dsa_boost": 0,
        "dev_boost": 1,          # Higher weight on production code and projects
        "urgency_multiplier": 1.15,
        "hours_per_proficiency_level": 28
    },
    "Early-stage Startup": {
        "dsa_boost": -1,
        "dev_boost": 2,          # Practical execution beats theoretical DSA
        "urgency_multiplier": 1.0,
        "hours_per_proficiency_level": 25
    },
    "Service-based": {
        "dsa_boost": -1,         # Basic DSA, strong emphasis on Aptitude & Communication
        "aptitude_boost": 1,
        "urgency_multiplier": 0.9,
        "hours_per_proficiency_level": 20
    },
    "Open to All": {
        "dsa_boost": 0,
        "urgency_multiplier": 1.0,
        "hours_per_proficiency_level": 25
    }
}


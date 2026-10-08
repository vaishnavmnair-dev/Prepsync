-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- SCRIPT 03: SEED DATA GENERATION
-- ============================================================================
-- Description: Realistic seed dataset representing the exact scenario from
-- the problem statement:
--   Student: Demo Student (1st Year, CSE (AI & ML))
--   Career Goal: Software Developer
--   Skills: DSA (1), C/C++ (3), Web Dev (1), DBMS (0)
--   Academic Workload: C Assignment (Tomorrow), Lab Record (Friday), Exam (Next week)
--   Available Time Today: 2.5 hours (150 mins)
--   Schedule: Classes 9:30 AM - 4:30 PM
-- ============================================================================

-- Clean up any existing demo records to ensure idempotency
DELETE FROM students WHERE student_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM career_roles WHERE role_id = '22222222-2222-2222-2222-222222222222';

-- ============================================================================
-- 1. SEED STUDENT PROFILE
-- ============================================================================
INSERT INTO students (
    student_id, full_name, email, college_name, degree, branch,
    current_year, current_semester, graduation_year,
    preferred_study_hours_per_day, daily_available_prep_minutes, timezone
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Demo Student',
    'demo.student@college.edu',
    'Apex Institute of Engineering & Technology',
    'B.Tech',
    'CSE (AI & ML)',
    1,
    1,
    2030,
    3.0,
    150,
    'Asia/Kolkata'
);

-- Initialize streak record
INSERT INTO student_streaks (
    streak_id, student_id, current_streak_days, longest_streak_days,
    total_study_minutes, total_tasks_completed, last_active_date
) VALUES (
    gen_random_uuid(),
    '11111111-1111-1111-1111-111111111111',
    4,
    7,
    580,
    14,
    CURRENT_DATE - INTERVAL '1 day'
);

-- ============================================================================
-- 2. SEED CAREER ROLES
-- ============================================================================
INSERT INTO career_roles (role_id, role_title, industry_domain, description, average_prep_duration_months)
VALUES
    ('22222222-2222-2222-2222-222222222222', 'Software Developer', 'Information Technology', 'Builds scalable software, data structures, algorithms, and system modules.', 8),
    (gen_random_uuid(), 'Frontend Developer', 'Web Engineering', 'Specializes in user interfaces, browser frameworks, and responsive UX.', 6),
    (gen_random_uuid(), 'Backend Developer', 'System Architecture', 'Specializes in distributed APIs, databases, microservices, and server logic.', 8),
    (gen_random_uuid(), 'Data Analyst', 'Data & Business Intelligence', 'Specializes in SQL, exploratory data analysis, business metrics, and visualization.', 5),
    (gen_random_uuid(), 'Data Scientist', 'AI & Data Science', 'Builds machine learning pipelines, statistical modeling, and data algorithms.', 10),
    (gen_random_uuid(), 'AI/ML Engineer', 'Artificial Intelligence', 'Deploys deep learning architectures, LLMs, computer vision, and neural models.', 10),
    (gen_random_uuid(), 'Cybersecurity Engineer', 'Information Security', 'Defends network perimeters, penetration testing, and secure software lifecycle.', 9)
ON CONFLICT (role_title) DO NOTHING;

-- Assign Demo Student Primary Career Goal
INSERT INTO student_career_goals (
    goal_id, student_id, role_id, target_company_type, target_placement_date, priority_rank, status, notes
) VALUES (
    gen_random_uuid(),
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'Product-based',
    '2029-07-01',
    1,
    'Active',
    'Targeting Tier-1 and Top Product firms for summer internship & on-campus placement.'
);

-- ============================================================================
-- 3. SEED SKILLS CATALOGUE
-- ============================================================================
INSERT INTO skills (skill_id, skill_name, category, description)
VALUES
    ('33333333-3333-3333-3333-000000000001', 'DSA', 'DSA', 'Data Structures and Algorithms: Arrays, Linked Lists, Trees, Graphs, DP, Complexity Analysis'),
    ('33333333-3333-3333-3333-000000000002', 'C/C++', 'Programming', 'C and C++ Programming, Memory Management, Pointers, and STL'),
    ('33333333-3333-3333-3333-000000000003', 'Web Development', 'Development', 'Full-stack fundamentals: HTML, CSS, JavaScript, and Modern Web Standards'),
    ('33333333-3333-3333-3333-000000000004', 'DBMS', 'Core CS', 'Database Management Systems: Relational Algebra, ER Modeling, Normalization, ACID'),
    ('33333333-3333-3333-3333-000000000005', 'Operating Systems', 'Core CS', 'Processes, Threads, CPU Scheduling, Virtual Memory, Concurrency & Deadlocks'),
    ('33333333-3333-3333-3333-000000000006', 'Computer Networks', 'Core CS', 'OSI 7 Layers, TCP/IP, Routing, Sockets, HTTP/HTTPS, DNS'),
    ('33333333-3333-3333-3333-000000000007', 'OOP', 'Core CS', 'Object-Oriented Programming: Encapsulation, Inheritance, Polymorphism, Abstraction, SOLID'),
    ('33333333-3333-3333-3333-000000000008', 'SQL', 'Core CS', 'Relational Queries, Joins, Aggregations, Indexing, Subqueries, Stored Procedures'),
    ('33333333-3333-3333-3333-000000000009', 'Git/GitHub', 'Development', 'Version Control, Branching, Pull Requests, Merge Conflict Resolution'),
    ('33333333-3333-3333-3333-000000000010', 'Aptitude', 'Aptitude', 'Quantitative Aptitude, Logical Reasoning, Verbal Ability for Placement Screening'),
    ('33333333-3333-3333-3333-000000000011', 'Communication', 'Soft Skills', 'Professional Communication, Technical Explanations, Team Collaboration'),
    ('33333333-3333-3333-3333-000000000012', 'Interview Preparation', 'Interview', 'Behavioral HR rounds, Mock Technical Interviews, STAR method'),
    ('33333333-3333-3333-3333-000000000013', 'Python', 'Programming', 'Python language syntax, standard library, scripting, and OOP'),
    ('33333333-3333-3333-3333-000000000014', 'JavaScript', 'Programming', 'Asynchronous JS, Event Loop, Closures, DOM, ES6+ features'),
    ('33333333-3333-3333-3333-000000000015', 'React', 'Development', 'Component Architecture, Hooks, State Management, Virtual DOM'),
    ('33333333-3333-3333-3333-000000000016', 'Node.js', 'Development', 'Server-side JavaScript, Express framework, REST APIs')
ON CONFLICT (skill_id) DO NOTHING;

-- ============================================================================
-- 4. SEED ROLE-SKILL REQUIREMENTS (FOR SOFTWARE DEVELOPER)
-- ============================================================================
-- Software Developer Requirements matching specification:
--   DSA -> High/Critical (Weight 10.0, Required 4)
--   C/C++ -> High (Weight 9.0, Required 4)
--   OOP -> High (Weight 8.5, Required 4)
--   DBMS -> Medium (Weight 7.5, Required 3)
--   Operating Systems -> Medium (Weight 7.0, Required 3)
--   Computer Networks -> Medium (Weight 6.5, Required 3)
--   Git/GitHub -> Medium (Weight 6.0, Required 3)
--   Development (Web Dev) -> Medium (Weight 6.5, Required 3)
--   Aptitude -> Medium (Weight 6.0, Required 3)
INSERT INTO role_skill_requirements (
    role_id, skill_id, required_proficiency, importance_level, weight_score, recommended_order, notes
) VALUES
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000001', 4, 'Critical', 10.0, 1, 'Core coding rounds and technical interviews test LeetCode medium/hard.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000002', 4, 'High',      9.0, 2, 'Primary language for speed, pointers, and memory manipulation in DSA.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000007', 4, 'High',      8.5, 3, 'Crucial for Low-Level Design (LLD) and clean software engineering.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000004', 3, 'Medium',    7.5, 4, 'Core CS rounds test transaction management and normalization.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000005', 3, 'Medium',    7.0, 5, 'Tested in technical interviews for multi-threading and process sync.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000006', 3, 'Medium',    6.5, 6, 'Protocols, sockets, and client-server communication questions.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000003', 3, 'Medium',    6.5, 7, 'Required for full-stack project building to showcase on resume.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000009', 3, 'Medium',    6.0, 8, 'Standard collaborative engineering requirement.'),
    ('22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-000000000010', 3, 'Medium',    6.0, 9, 'First-round online assessment (OA) test filter.')
ON CONFLICT (role_id, skill_id) DO NOTHING;

-- ============================================================================
-- 5. SEED STUDENT SKILL ASSESSMENTS (EXACT SCENARIO)
-- ============================================================================
-- DSA: Beginner (1) -> Target 4 -> Gap = 3
-- C/C++: Intermediate (3) -> Target 4 -> Gap = 1
-- Web Development: Beginner (1) -> Target 3 -> Gap = 2
-- DBMS: Not Started (0) -> Target 3 -> Gap = 3
INSERT INTO student_skills (
    student_id, skill_id, current_proficiency, target_proficiency, confidence_level, assessment_source, notes
) VALUES
    ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-000000000001', 1, 4, 'Medium', 'Self Assessment', 'Basic syntax understood; struggle with recursion and binary trees.'),
    ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-000000000002', 3, 4, 'High',   'Completed Course', 'Comfortable with pointers, structs, dynamic memory, and basic STL vectors.'),
    ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-000000000003', 1, 3, 'Medium', 'Self Assessment', 'Know HTML tags and basic CSS styling; JavaScript event handling is new.'),
    ('11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-000000000004', 0, 3, 'Low',    'Self Assessment', 'Not started yet; have not taken college DBMS class.')
ON CONFLICT (student_id, skill_id) DO UPDATE SET
    current_proficiency = EXCLUDED.current_proficiency,
    target_proficiency = EXCLUDED.target_proficiency;

-- ============================================================================
-- 6. SEED COLLEGE ACADEMIC WORKLOAD (EXACT SCENARIO)
-- ============================================================================
-- C assignment: due tomorrow (45 mins)
-- Lab record: due Friday (60 mins)
-- Internal exam: next week (180 mins)
INSERT INTO academic_tasks (
    task_id, student_id, subject, task_title, description, task_type,
    priority, estimated_duration_minutes, remaining_duration_minutes,
    deadline, status, completion_percentage, difficulty
) VALUES
    (
        '44444444-4444-4444-4444-000000000001',
        '11111111-1111-1111-1111-111111111111',
        'C Programming',
        'C Programming Assignment 3: Pointers & Structs',
        'Implement dynamic struct array allocation for student record management system.',
        'Assignment',
        'High',
        45,
        45,
        CURRENT_DATE + INTERVAL '1 day' + TIME '23:59:00',
        'In Progress',
        10,
        'Medium'
    ),
    (
        '44444444-4444-4444-4444-000000000002',
        '11111111-1111-1111-1111-111111111111',
        'Physics Lab',
        'Optics & Laser Diffraction Lab Record',
        'Complete tabular observations, error percentage calculations, and graph plots.',
        'Lab',
        'High',
        60,
        60,
        CURRENT_DATE + (5 - EXTRACT(DOW FROM CURRENT_DATE))::INT * INTERVAL '1 day' + TIME '17:00:00',
        'Not Started',
        0,
        'Easy'
    ),
    (
        '44444444-4444-4444-4444-000000000003',
        '11111111-1111-1111-1111-111111111111',
        'Discrete Mathematics',
        'First Sessional Internal Examination',
        'Comprehensive syllabus covering Propositional Logic, Sets, Relations, and Proof by Induction.',
        'Exam',
        'Critical',
        180,
        180,
        CURRENT_DATE + INTERVAL '7 days' + TIME '09:30:00',
        'Not Started',
        0,
        'Hard'
    )
ON CONFLICT (task_id) DO NOTHING;

-- ============================================================================
-- 7. SEED COLLEGE SCHEDULE (9:30 AM – 4:30 PM TIMETABLE)
-- ============================================================================
INSERT INTO student_schedule (
    schedule_id, student_id, day_of_week, start_time, end_time,
    activity_name, activity_type, location_or_room
)
SELECT
    gen_random_uuid(),
    '11111111-1111-1111-1111-111111111111',
    day_name,
    start_t,
    end_t,
    act_name,
    act_type,
    loc
FROM (
    VALUES
        ('09:30'::TIME, '10:30'::TIME, 'Discrete Mathematics', 'Lecture', 'LH-201'),
        ('10:30'::TIME, '11:30'::TIME, 'C Programming', 'Lecture', 'LH-203'),
        ('12:00'::TIME, '13:00'::TIME, 'Engineering Physics', 'Lecture', 'LH-105'),
        ('14:00'::TIME, '16:30'::TIME, 'Programming & Data Structures Lab', 'Lab', 'Lab-3')
) AS timetable(start_t, end_t, act_name, act_type, loc)
CROSS JOIN (
    VALUES ('Monday'), ('Tuesday'), ('Wednesday'), ('Thursday'), ('Friday')
) AS days(day_name);

-- ============================================================================
-- 8. SEED AVAILABLE STUDY TIME TODAY (2.5 HOURS / 150 MINUTES)
-- ============================================================================
INSERT INTO study_availability (
    availability_id, student_id, availability_date,
    available_start_time, available_end_time, available_duration_minutes,
    energy_level, preferred_activity, notes
) VALUES (
    gen_random_uuid(),
    '11111111-1111-1111-1111-111111111111',
    CURRENT_DATE,
    '18:30:00',
    '21:00:00',
    150,
    'Medium',
    'Mixed',
    'Post-college evening block. Balanced focus on urgent assignment and core DSA prep.'
);

-- ============================================================================
-- 9. SEED LEARNING RESOURCES CATALOGUE
-- ============================================================================
INSERT INTO learning_resources (
    resource_id, skill_id, title, resource_type, url,
    difficulty, estimated_duration_minutes, provider, description
) VALUES
    (
        gen_random_uuid(),
        '33333333-3333-3333-3333-000000000001',
        'Arrays & Two-Pointer Pattern Crash Course',
        'Video',
        'https://neetcode.io/practice',
        'Beginner',
        45,
        'NeetCode',
        'Visual intuition for Two Pointers, Sliding Window, and In-place array operations.'
    ),
    (
        gen_random_uuid(),
        '33333333-3333-3333-3333-000000000004',
        'Relational Database Modeling & ACID Properties',
        'Course',
        'https://coursera.org/learn/dbms-basics',
        'Beginner',
        30,
        'Coursera / Meta',
        'Core principles of entities, relations, primary/foreign keys, and transactions.'
    ),
    (
        gen_random_uuid(),
        '33333333-3333-3333-3333-000000000003',
        'Modern Responsive CSS Grid & Flexbox Masterclass',
        'Practice Set',
        'https://developer.mozilla.org/en-US/docs/Learn/CSS',
        'Beginner',
        30,
        'MDN Web Docs',
        'Hands-on styling exercises for responsive modern web layouts.'
    );

-- ============================================================================
-- 10. SEED PLACEMENT LEARNING TASKS
-- ============================================================================
INSERT INTO learning_tasks (
    task_id, student_id, skill_id, title, description,
    estimated_duration_minutes, remaining_duration_minutes,
    difficulty, priority, status, completion_percentage
) VALUES
    (
        '55555555-5555-5555-5555-000000000001',
        '11111111-1111-1111-1111-111111111111',
        '33333333-3333-3333-3333-000000000001',
        'Practice 5 LeetCode Array Problems (Two Pointers)',
        'Solve Two Sum, 3Sum, Valid Palindrome, and Container With Most Water.',
        45,
        45,
        'Beginner',
        9,
        'Not Started',
        0
    ),
    (
        '55555555-5555-5555-5555-000000000002',
        '11111111-1111-1111-1111-111111111111',
        '33333333-3333-3333-3333-000000000004',
        'Study DBMS Basics: ER Models & ACID Rules',
        'Read notes on Database Transactions, Atomicity, and Normal Forms 1NF to 3NF.',
        30,
        30,
        'Beginner',
        7,
        'Not Started',
        0
    ),
    (
        '55555555-5555-5555-5555-000000000003',
        '11111111-1111-1111-1111-111111111111',
        '33333333-3333-3333-3333-000000000003',
        'Build Responsive Student Portfolio Web Page',
        'Create a lightweight profile showcase demonstrating HTML semantics and CSS Flexbox.',
        30,
        30,
        'Beginner',
        6,
        'Not Started',
        0
    )
ON CONFLICT (task_id) DO NOTHING;

-- ============================================================================
-- 11. SEED TODAY'S DAILY PLAN & SCHEDULED PLAN ITEMS
-- ============================================================================
INSERT INTO daily_plans (
    plan_id, student_id, plan_date,
    total_available_minutes, total_planned_minutes,
    academic_workload_minutes, placement_prep_minutes,
    plan_status, ai_reasoning
) VALUES (
    '66666666-6666-6666-6666-000000000001',
    '11111111-1111-1111-1111-111111111111',
    CURRENT_DATE,
    150,
    150,
    45,
    105,
    'Active',
    'The student has 150 minutes available with medium energy. Academic priority goes to C Assignment (due tomorrow, 45m). Remaining 105 minutes is allocated directly to top placement gaps for Software Developer: DSA Arrays (gap=3, 45m), unstarted DBMS basics (gap=3, 30m), and Web Development practice (30m).'
)
ON CONFLICT (student_id, plan_date) DO UPDATE SET
    total_planned_minutes = EXCLUDED.total_planned_minutes,
    ai_reasoning = EXCLUDED.ai_reasoning;

-- Plan Item 1: Academic (C Assignment)
INSERT INTO daily_plan_items (
    plan_item_id, plan_id, task_category, academic_task_id, learning_task_id,
    custom_title, scheduled_start_time, scheduled_end_time,
    planned_duration_minutes, actual_duration_minutes,
    priority_score, ai_item_reasoning, status, completion_percentage, item_order
) VALUES (
    '77777777-7777-7777-7777-000000000001',
    '66666666-6666-6666-6666-000000000001',
    'Academic',
    '44444444-4444-4444-4444-000000000001',
    NULL,
    'C Assignment: Structs & Dynamic Memory',
    '18:30:00',
    '19:15:00',
    45,
    0,
    10.00,
    'Urgent college deadline: Due tomorrow. Clearing this first prevents academic penalties and frees mental focus.',
    'Scheduled',
    0,
    1
),
-- Plan Item 2: Placement (DSA Arrays)
(
    '77777777-7777-7777-7777-000000000002',
    '66666666-6666-6666-6666-000000000001',
    'Placement',
    NULL,
    '55555555-5555-5555-5555-000000000001',
    'DSA: Practice Array Two-Pointer Problems',
    '19:20:00',
    '20:05:00',
    45,
    0,
    9.00,
    'Top priority career skill with largest gap (level 1 -> target 4). Highest role weight (10.0) for Software Developer.',
    'Scheduled',
    0,
    2
),
-- Plan Item 3: Placement (DBMS Basics)
(
    '77777777-7777-7777-7777-000000000003',
    '66666666-6666-6666-6666-000000000001',
    'Placement',
    NULL,
    '55555555-5555-5555-5555-000000000002',
    'DBMS: Study Relational Model & ACID Rules',
    '20:10:00',
    '20:40:00',
    30,
    0,
    7.50,
    'Skill is currently at Level 0 (Not Started). Quick 30m foundational session bootstraps the learning curve.',
    'Scheduled',
    0,
    3
),
-- Plan Item 4: Placement (Web Dev Layout)
(
    '77777777-7777-7777-7777-000000000004',
    '66666666-6666-6666-6666-000000000001',
    'Placement',
    NULL,
    '55555555-5555-5555-5555-000000000003',
    'Web Dev: Build Responsive Portfolio Layout',
    '20:40:00',
    '21:10:00',
    30,
    0,
    6.50,
    'Lightweight visual coding session suitable for lower cognitive energy towards the end of the evening.',
    'Scheduled',
    0,
    4
)
ON CONFLICT (plan_item_id) DO NOTHING;

-- ============================================================================
-- 12. SEED HISTORICAL PROGRESS LOGS
-- ============================================================================
INSERT INTO progress_logs (
    student_id, task_category, academic_task_id, learning_task_id, skill_id,
    log_date, session_start_time, session_end_time, time_spent_minutes,
    problems_completed, previous_proficiency, new_proficiency, completion_percentage, notes
) VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'Placement',
        NULL,
        '55555555-5555-5555-5555-000000000001',
        '33333333-3333-3333-3333-000000000002',
        CURRENT_DATE - INTERVAL '2 days',
        CURRENT_TIMESTAMP - INTERVAL '2 days',
        CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '60 minutes',
        60,
        4,
        2,
        3,
        100,
        'Mastered C++ pointers and memory references. Proficiency upgraded from Basic (2) to Intermediate (3).'
    ),
    (
        '11111111-1111-1111-1111-111111111111',
        'Academic',
        '44444444-4444-4444-4444-000000000001',
        NULL,
        '33333333-3333-3333-3333-000000000002',
        CURRENT_DATE - INTERVAL '1 day',
        CURRENT_TIMESTAMP - INTERVAL '1 day',
        CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '45 minutes',
        45,
        0,
        3,
        3,
        30,
        'Drafted header files and struct definitions for C Assignment 3.'
    );

-- ============================================================================
-- 13. SEED ADAPTATION AUDIT & AI RECOMMENDATIONS
-- ============================================================================
INSERT INTO plan_adaptations (
    plan_id, student_id, plan_item_id, trigger_event, adaptation_type,
    original_duration_minutes, adapted_duration_minutes, ai_adaptation_reason
) VALUES (
    '66666666-6666-6666-6666-000000000001',
    '11111111-1111-1111-1111-111111111111',
    '77777777-7777-7777-7777-000000000002',
    'Energy Drop',
    'Duration Adjusted',
    60,
    45,
    'Student indicated Medium energy level post 7-hour college schedule. Reduced DSA block from 60m to 45m to prevent cognitive fatigue.'
);

INSERT INTO ai_recommendations (
    student_id, recommendation_type, context_reference, recommendation_text, priority, status
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Workload Warning',
    '{"assignment_due_in_hours": 36, "active_academic_tasks": 3}'::jsonb,
    'You have C Assignment due tomorrow and Physics Lab due on Friday. We scheduled C Assignment first today so you can focus on DSA uninterrupted tomorrow.',
    'High',
    'Accepted'
),
(
    '11111111-1111-1111-1111-111111111111',
    'Skill Gap Recommendation',
    '{"skill": "DBMS", "current_level": 0, "target_level": 3}'::jsonb,
    'DBMS has not been started (Level 0). We recommend starting with 30 minutes of Relational Theory today to lay the groundwork for SQL queries.',
    'Medium',
    'Accepted'
);

-- ============================================================================
-- 14. SEED NOTIFICATIONS
-- ============================================================================
INSERT INTO notifications (
    student_id, notification_type, title, message, related_task_category, related_task_id, scheduled_time, is_read
) VALUES
    (
        '11111111-1111-1111-1111-111111111111',
        'Deadline Reminder',
        'Upcoming Deadline: C Programming Assignment 3',
        'Your C Programming Assignment 3 is due tomorrow night. Please finish the 45-minute scheduled block today.',
        'Academic',
        '44444444-4444-4444-4444-000000000001',
        CURRENT_TIMESTAMP,
        FALSE
    ),
    (
        '11111111-1111-1111-1111-111111111111',
        'Daily Plan Ready',
        'Your Balanced Plan for Today is Active',
        'Today includes 45m academic work and 105m placement prep across DSA, DBMS, and Web Dev.',
        NULL,
        NULL,
        CURRENT_TIMESTAMP,
        TRUE
    );


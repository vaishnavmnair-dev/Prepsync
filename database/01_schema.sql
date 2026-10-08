-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- SCRIPT 01: POSTGRESQL SCHEMA DEFINITION
-- ============================================================================
-- Description: Core relational schema with normalized tables, UUID primary keys,
-- foreign keys, check constraints, composite indexes, and audit triggers.
-- Database Target: PostgreSQL 14+
-- ============================================================================

-- Enable UUID extension for cryptographically secure, collision-free identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. UTILITY FUNCTIONS & AUDIT TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 2. STUDENT / USER MANAGEMENT
-- ============================================================================

CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    college_name VARCHAR(255) NOT NULL,
    degree VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    current_year SMALLINT NOT NULL CHECK (current_year BETWEEN 1 AND 5),
    current_semester SMALLINT NOT NULL CHECK (current_semester BETWEEN 1 AND 10),
    graduation_year INT NOT NULL CHECK (graduation_year >= 2024),
    preferred_study_hours_per_day NUMERIC(3, 1) NOT NULL DEFAULT 3.0 CHECK (preferred_study_hours_per_day >= 0.0 AND preferred_study_hours_per_day <= 18.0),
    daily_available_prep_minutes INT NOT NULL DEFAULT 150 CHECK (daily_available_prep_minutes >= 0 AND daily_available_prep_minutes <= 1440),
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Kolkata',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_students_updated_at
BEFORE UPDATE ON students
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 3. CAREER ROLES & STUDENT CAREER GOALS
-- ============================================================================

-- Central reference table of standard career roles (e.g., Software Developer, AI/ML)
CREATE TABLE career_roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_title VARCHAR(150) NOT NULL UNIQUE,
    industry_domain VARCHAR(100) NOT NULL DEFAULT 'Information Technology',
    description TEXT,
    average_prep_duration_months INT DEFAULT 6 CHECK (average_prep_duration_months > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_career_roles_updated_at
BEFORE UPDATE ON career_roles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Student career aspirations (Supports multiple career goals with priority rank)
CREATE TABLE student_career_goals (
    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES career_roles(role_id) ON DELETE RESTRICT,
    target_company_type VARCHAR(100) NOT NULL CHECK (target_company_type IN (
        'Product-based',
        'FAANG / Tier-1',
        'Service-based',
        'Early-stage Startup',
        'Unicorn Startup',
        'Open to All'
    )),
    target_placement_date DATE NOT NULL,
    priority_rank SMALLINT NOT NULL DEFAULT 1 CHECK (priority_rank > 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Paused', 'Achieved', 'Abandoned')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_role UNIQUE (student_id, role_id)
);

CREATE TRIGGER trg_student_career_goals_updated_at
BEFORE UPDATE ON student_career_goals
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. SKILLS CATALOGUE & CAREER-SKILL REQUIREMENTS
-- ============================================================================

CREATE TABLE skills (
    skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'Programming',
        'DSA',
        'Development',
        'Core CS',
        'Aptitude',
        'Interview',
        'Soft Skills'
    )),
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Requirement matrix mapping career roles to required skills
CREATE TABLE role_skill_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES career_roles(role_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    required_proficiency SMALLINT NOT NULL CHECK (required_proficiency BETWEEN 0 AND 5),
    importance_level VARCHAR(20) NOT NULL CHECK (importance_level IN ('Critical', 'High', 'Medium', 'Low')),
    weight_score NUMERIC(3, 1) NOT NULL DEFAULT 5.0 CHECK (weight_score BETWEEN 1.0 AND 10.0),
    recommended_order SMALLINT NOT NULL DEFAULT 1 CHECK (recommended_order > 0),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_role_skill UNIQUE (role_id, skill_id)
);

-- ============================================================================
-- 5. STUDENT SKILL ASSESSMENT
-- ============================================================================

-- Proficiency scale:
-- 0 = Not Started, 1 = Beginner, 2 = Basic, 3 = Intermediate, 4 = Advanced, 5 = Expert
CREATE TABLE student_skills (
    student_skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    current_proficiency SMALLINT NOT NULL DEFAULT 0 CHECK (current_proficiency BETWEEN 0 AND 5),
    target_proficiency SMALLINT NOT NULL DEFAULT 4 CHECK (target_proficiency BETWEEN 0 AND 5),
    confidence_level VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (confidence_level IN ('Low', 'Medium', 'High')),
    last_assessed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assessment_source VARCHAR(50) NOT NULL DEFAULT 'Self Assessment' CHECK (assessment_source IN (
        'Self Assessment',
        'Quiz',
        'AI Assessment',
        'Completed Course',
        'Project',
        'Interview'
    )),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_skill UNIQUE (student_id, skill_id),
    CONSTRAINT chk_target_gte_current CHECK (target_proficiency >= current_proficiency)
);

CREATE TRIGGER trg_student_skills_updated_at
BEFORE UPDATE ON student_skills
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 6. COLLEGE ACADEMIC WORKLOAD
-- ============================================================================

CREATE TABLE academic_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    subject VARCHAR(150) NOT NULL,
    task_title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN (
        'Assignment',
        'Lab',
        'Exam',
        'Project',
        'Practical',
        'Quiz',
        'Presentation',
        'Other'
    )),
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    estimated_duration_minutes INT NOT NULL CHECK (estimated_duration_minutes > 0),
    remaining_duration_minutes INT NOT NULL CHECK (remaining_duration_minutes >= 0),
    start_date DATE,
    deadline TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'In Progress', 'Completed', 'Overdue', 'Cancelled')),
    completion_percentage SMALLINT NOT NULL DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    difficulty VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_pattern VARCHAR(50),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_academic_remaining_le_estimated CHECK (remaining_duration_minutes <= estimated_duration_minutes)
);

CREATE TRIGGER trg_academic_tasks_updated_at
BEFORE UPDATE ON academic_tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. COLLEGE SCHEDULE (TIMETABLE / COMMITMENTS)
-- ============================================================================

CREATE TABLE student_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL CHECK (day_of_week IN (
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    )),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    activity_name VARCHAR(150) NOT NULL,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'Lecture', 'Lab', 'Tutorial', 'Sports', 'Transit', 'Other'
    )),
    is_recurring BOOLEAN NOT NULL DEFAULT TRUE,
    location_or_room VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_schedule_end_after_start CHECK (end_time > start_time)
);

CREATE TRIGGER trg_student_schedule_updated_at
BEFORE UPDATE ON student_schedule
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. AVAILABLE STUDY TIME
-- ============================================================================

CREATE TABLE study_availability (
    availability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    availability_date DATE NOT NULL,
    available_start_time TIME NOT NULL,
    available_end_time TIME NOT NULL,
    available_duration_minutes INT NOT NULL CHECK (available_duration_minutes > 0),
    energy_level VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (energy_level IN ('Low', 'Medium', 'High')),
    preferred_activity VARCHAR(50) NOT NULL DEFAULT 'Mixed' CHECK (preferred_activity IN (
        'Placement Prep', 'Academic Workload', 'Mixed', 'Revision', 'Problem Solving'
    )),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_avail_end_after_start CHECK (available_end_time > available_start_time)
);

-- ============================================================================
-- 9. LEARNING RESOURCES CATALOGUE
-- ============================================================================

CREATE TABLE learning_resources (
    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN (
        'Video', 'Course', 'Article', 'Documentation', 'Practice Set', 'Problem Set', 'Project', 'Quiz'
    )),
    url TEXT,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    estimated_duration_minutes INT NOT NULL CHECK (estimated_duration_minutes > 0),
    provider VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. LEARNING TASKS (PLACEMENT PREPARATION WORKLOAD)
-- ============================================================================

CREATE TABLE learning_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    resource_id UUID REFERENCES learning_resources(resource_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    estimated_duration_minutes INT NOT NULL CHECK (estimated_duration_minutes > 0),
    remaining_duration_minutes INT NOT NULL CHECK (remaining_duration_minutes >= 0),
    difficulty VARCHAR(20) NOT NULL DEFAULT 'Intermediate' CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    priority SMALLINT NOT NULL DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status VARCHAR(30) NOT NULL DEFAULT 'Not Started' CHECK (status IN (
        'Not Started', 'In Progress', 'Completed', 'Deferred', 'Cancelled'
    )),
    completion_percentage SMALLINT NOT NULL DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    deadline TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_learning_remaining_le_estimated CHECK (remaining_duration_minutes <= estimated_duration_minutes)
);

CREATE TRIGGER trg_learning_tasks_updated_at
BEFORE UPDATE ON learning_tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 11. DAILY PLANS & DAILY PLAN ITEMS
-- ============================================================================

CREATE TABLE daily_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    plan_date DATE NOT NULL,
    total_available_minutes INT NOT NULL CHECK (total_available_minutes >= 0),
    total_planned_minutes INT NOT NULL CHECK (total_planned_minutes >= 0),
    academic_workload_minutes INT NOT NULL DEFAULT 0 CHECK (academic_workload_minutes >= 0),
    placement_prep_minutes INT NOT NULL DEFAULT 0 CHECK (placement_prep_minutes >= 0),
    plan_status VARCHAR(30) NOT NULL DEFAULT 'Generated' CHECK (plan_status IN (
        'Draft', 'Generated', 'Active', 'Completed', 'Partially Completed', 'Cancelled'
    )),
    ai_reasoning TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_plan_date UNIQUE (student_id, plan_date)
);

CREATE TRIGGER trg_daily_plans_updated_at
BEFORE UPDATE ON daily_plans
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE daily_plan_items (
    plan_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES daily_plans(plan_id) ON DELETE CASCADE,
    task_category VARCHAR(20) NOT NULL CHECK (task_category IN ('Academic', 'Placement')),
    academic_task_id UUID REFERENCES academic_tasks(task_id) ON DELETE SET NULL,
    learning_task_id UUID REFERENCES learning_tasks(task_id) ON DELETE SET NULL,
    custom_title VARCHAR(255) NOT NULL,
    scheduled_start_time TIME,
    scheduled_end_time TIME,
    planned_duration_minutes INT NOT NULL CHECK (planned_duration_minutes > 0),
    actual_duration_minutes INT NOT NULL DEFAULT 0 CHECK (actual_duration_minutes >= 0),
    priority_score NUMERIC(4, 2) NOT NULL CHECK (priority_score BETWEEN 1.00 AND 10.00),
    ai_item_reasoning TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Scheduled' CHECK (status IN (
        'Scheduled', 'In Progress', 'Completed', 'Partially Completed', 'Missed', 'Rescheduled'
    )),
    completion_percentage SMALLINT NOT NULL DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    item_order SMALLINT NOT NULL DEFAULT 1 CHECK (item_order > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_plan_item_polymorphic CHECK (
        (task_category = 'Academic' AND academic_task_id IS NOT NULL AND learning_task_id IS NULL)
        OR
        (task_category = 'Placement' AND learning_task_id IS NOT NULL AND academic_task_id IS NULL)
    )
);

CREATE TRIGGER trg_daily_plan_items_updated_at
BEFORE UPDATE ON daily_plan_items
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 12. PROGRESS TRACKING & STREAKS
-- ============================================================================

CREATE TABLE progress_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    task_category VARCHAR(20) NOT NULL CHECK (task_category IN ('Academic', 'Placement')),
    academic_task_id UUID REFERENCES academic_tasks(task_id) ON DELETE SET NULL,
    learning_task_id UUID REFERENCES learning_tasks(task_id) ON DELETE SET NULL,
    skill_id UUID REFERENCES skills(skill_id) ON DELETE SET NULL,
    log_date DATE NOT NULL DEFAULT CURRENT_DATE,
    session_start_time TIMESTAMPTZ,
    session_end_time TIMESTAMPTZ,
    time_spent_minutes INT NOT NULL CHECK (time_spent_minutes > 0),
    problems_completed INT NOT NULL DEFAULT 0 CHECK (problems_completed >= 0),
    previous_proficiency SMALLINT CHECK (previous_proficiency BETWEEN 0 AND 5),
    new_proficiency SMALLINT CHECK (new_proficiency BETWEEN 0 AND 5),
    completion_percentage SMALLINT NOT NULL DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_streaks (
    streak_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,
    current_streak_days INT NOT NULL DEFAULT 0 CHECK (current_streak_days >= 0),
    longest_streak_days INT NOT NULL DEFAULT 0 CHECK (longest_streak_days >= 0),
    total_study_minutes INT NOT NULL DEFAULT 0 CHECK (total_study_minutes >= 0),
    total_tasks_completed INT NOT NULL DEFAULT 0 CHECK (total_tasks_completed >= 0),
    last_active_date DATE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 13. PLAN ADAPTATION & AUDIT HISTORY
-- ============================================================================

CREATE TABLE plan_adaptations (
    adaptation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES daily_plans(plan_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    plan_item_id UUID REFERENCES daily_plan_items(plan_item_id) ON DELETE SET NULL,
    trigger_event VARCHAR(50) NOT NULL CHECK (trigger_event IN (
        'Task Missed',
        'Task Partial Completion',
        'Emergency Workload Added',
        'Deadline Shift',
        'Energy Drop',
        'User Request',
        'Overdue Task Escalation'
    )),
    adaptation_type VARCHAR(50) NOT NULL CHECK (adaptation_type IN (
        'Rescheduled',
        'Duration Adjusted',
        'Task Deferred',
        'Task Replaced',
        'Workload Warning Triggered',
        'Priority Re-ordered'
    )),
    original_duration_minutes INT,
    adapted_duration_minutes INT,
    rescheduled_to_date DATE,
    ai_adaptation_reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 14. AI RECOMMENDATION HISTORY
-- ============================================================================

CREATE TABLE ai_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL CHECK (recommendation_type IN (
        'Daily Plan',
        'Skill Recommendation',
        'Career Recommendation',
        'Workload Warning',
        'Deadline Warning',
        'Study Recommendation',
        'Skill Gap Recommendation',
        'Burnout Prevention'
    )),
    context_reference JSONB,
    recommendation_text TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending' CHECK (status IN (
        'Pending', 'Accepted', 'Rejected', 'Dismissed', 'Auto-Applied'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actioned_at TIMESTAMPTZ
);

-- ============================================================================
-- 15. NOTIFICATIONS & REMINDERS
-- ============================================================================

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN (
        'Deadline Reminder',
        'Exam Reminder',
        'Daily Plan Ready',
        'Missed Task Alert',
        'Study Session Prompt',
        'Weekly Summary',
        'Burnout Warning'
    )),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_task_category VARCHAR(20) CHECK (related_task_category IN ('Academic', 'Placement')),
    related_task_id UUID,
    scheduled_time TIMESTAMPTZ NOT NULL,
    sent_time TIMESTAMPTZ,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 16. INDEXES FOR PERFORMANCE & QUERY ACCELERATION
-- ============================================================================

-- Students indexes
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_college_branch ON students(college_name, branch);

-- Career Goals & Skills indexes
CREATE INDEX idx_student_career_goals_lookup ON student_career_goals(student_id, priority_rank) WHERE status = 'Active';
CREATE INDEX idx_role_skill_req_role_importance ON role_skill_requirements(role_id, importance_level, recommended_order);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_student_skills_student ON student_skills(student_id, current_proficiency);

-- Academic Workload & Deadlines (Critical for AI Urgency Calculation)
CREATE INDEX idx_academic_tasks_student_deadline ON academic_tasks(student_id, deadline ASC) WHERE status NOT IN ('Completed', 'Cancelled');
CREATE INDEX idx_academic_tasks_status ON academic_tasks(status);

-- Timetable & Availability
CREATE INDEX idx_student_schedule_day ON student_schedule(student_id, day_of_week);
CREATE INDEX idx_study_availability_date ON study_availability(student_id, availability_date);

-- Learning Tasks & Resources
CREATE INDEX idx_learning_tasks_student_skill ON learning_tasks(student_id, skill_id, priority DESC) WHERE status NOT IN ('Completed', 'Cancelled');
CREATE INDEX idx_learning_resources_skill_diff ON learning_resources(skill_id, difficulty);

-- Daily Plans & Items
CREATE INDEX idx_daily_plans_student_date ON daily_plans(student_id, plan_date);
CREATE INDEX idx_daily_plan_items_plan ON daily_plan_items(plan_id, item_order ASC);
CREATE INDEX idx_daily_plan_items_status ON daily_plan_items(status);

-- Progress & Analytics
CREATE INDEX idx_progress_logs_student_date ON progress_logs(student_id, log_date DESC);
CREATE INDEX idx_progress_logs_skill ON progress_logs(student_id, skill_id);

-- Adaptations & Recommendations
CREATE INDEX idx_plan_adaptations_student ON plan_adaptations(student_id, created_at DESC);
CREATE INDEX idx_ai_recommendations_student ON ai_recommendations(student_id, status, created_at DESC);
CREATE INDEX idx_notifications_pending ON notifications(student_id, scheduled_time ASC) WHERE is_read = FALSE;


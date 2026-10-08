-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- SCRIPT 05: MASTER AI PLANNING CONTEXT QUERY & JSON COMPILER
-- ============================================================================
-- Description: Consolidated query returning the complete multi-dimensional
-- context needed by the AI Agent to build a realistic, balanced daily plan.
--
-- Core Product Question Answered:
-- "Given this student's career goal, current skill level, college workload,
--  upcoming deadlines, available study time and recent progress, what
--  information does the AI need to generate the most realistic plan for today?"
-- ============================================================================

-- ============================================================================
-- METHOD 1: CALL THE COMPILED POSTGRESQL FUNCTION
-- ============================================================================
SELECT fn_get_ai_daily_plan_context(
    '11111111-1111-1111-1111-111111111111'::UUID,
    CURRENT_DATE
) AS ai_planning_payload;

-- ============================================================================
-- METHOD 2: DIRECT PURE-SQL CONTEXT QUERY (SINGLE STATEMENT)
-- Useful for backend frameworks (Node.js pg, Python asyncpg, Prisma, etc.)
-- ============================================================================
WITH
student_data AS (
    SELECT
        s.student_id,
        s.full_name,
        s.college_name,
        s.degree,
        s.branch,
        s.current_year,
        s.current_semester,
        s.graduation_year,
        s.preferred_study_hours_per_day,
        s.daily_available_prep_minutes,
        s.timezone
    FROM students s
    WHERE s.student_id = '11111111-1111-1111-1111-111111111111'
),
career_context AS (
    SELECT
        cr.role_title AS primary_goal,
        scg.target_company_type,
        scg.target_placement_date,
        scg.priority_rank
    FROM student_career_goals scg
    JOIN career_roles cr ON scg.role_id = cr.role_id
    WHERE scg.student_id = '11111111-1111-1111-1111-111111111111'
      AND scg.priority_rank = 1
      AND scg.status = 'Active'
    LIMIT 1
),
availability_today AS (
    SELECT
        sa.available_start_time,
        sa.available_end_time,
        sa.available_duration_minutes,
        sa.energy_level,
        sa.preferred_activity,
        sa.notes
    FROM study_availability sa
    WHERE sa.student_id = '11111111-1111-1111-1111-111111111111'
      AND sa.availability_date = CURRENT_DATE
),
skill_gaps_ranked AS (
    SELECT
        vsg.skill_name,
        vsg.skill_category,
        vsg.current_proficiency,
        vsg.required_proficiency,
        vsg.skill_gap,
        vsg.importance_level,
        vsg.gap_urgency_score
    FROM v_student_skill_gaps vsg
    WHERE vsg.student_id = '11111111-1111-1111-1111-111111111111'
      AND vsg.skill_gap > 0
    ORDER BY vsg.gap_urgency_score DESC
),
academic_tasks_urgent AS (
    SELECT
        vaw.task_id,
        vaw.subject,
        vaw.task_title,
        vaw.task_type,
        vaw.deadline,
        vaw.hours_until_deadline,
        vaw.remaining_duration_minutes,
        vaw.deadline_urgency_category,
        vaw.status
    FROM v_student_active_workload vaw
    WHERE vaw.student_id = '11111111-1111-1111-1111-111111111111'
    ORDER BY vaw.deadline ASC
),
placement_tasks_pending AS (
    SELECT
        lt.task_id,
        sk.skill_name,
        lt.title AS task_title,
        lt.difficulty,
        lt.priority,
        lt.remaining_duration_minutes,
        lt.status
    FROM learning_tasks lt
    JOIN skills sk ON lt.skill_id = sk.skill_id
    WHERE lt.student_id = '11111111-1111-1111-1111-111111111111'
      AND lt.status NOT IN ('Completed', 'Cancelled')
    ORDER BY lt.priority DESC, lt.remaining_duration_minutes ASC
),
recent_progress AS (
    SELECT
        vwp.total_study_hours_last_7d,
        vwp.academic_minutes_last_7d,
        vwp.placement_minutes_last_7d,
        vwp.coding_problems_solved_last_7d,
        vwp.current_streak_days
    FROM v_student_weekly_progress vwp
    WHERE vwp.student_id = '11111111-1111-1111-1111-111111111111'
)
SELECT json_build_object(
    'generated_at', CURRENT_TIMESTAMP,
    'student', (SELECT row_to_json(sd) FROM student_data sd),
    'career_goal', (SELECT row_to_json(cc) FROM career_context cc),
    'today_availability', (SELECT row_to_json(av) FROM availability_today av),
    'priority_skill_gaps', (SELECT json_agg(sg) FROM skill_gaps_ranked sg),
    'academic_deadlines', (SELECT json_agg(at) FROM academic_tasks_urgent at),
    'pending_placement_tasks', (SELECT json_agg(pt) FROM placement_tasks_pending pt),
    'recent_progress', (SELECT row_to_json(rp) FROM recent_progress rp)
) AS ai_daily_context_json;


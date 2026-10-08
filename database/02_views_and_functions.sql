-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- SCRIPT 02: DATABASE VIEWS & AI CONTEXT FUNCTIONS
-- ============================================================================
-- Description: Standard views for calculating skill gaps, workload urgency,
-- historical progress, and a dedicated JSON generator function providing
-- structured context directly to the AI planning agent.
-- ============================================================================

-- ============================================================================
-- VIEW 1: STUDENT SKILL GAPS (CAREER-ALIGNED)
-- ============================================================================
-- Calculates gap between target career requirement and current proficiency.
-- Urgency Score = (Skill Gap) * (Requirement Weight Score).
CREATE OR REPLACE VIEW v_student_skill_gaps AS
SELECT
    s.student_id,
    s.full_name,
    cr.role_id,
    cr.role_title,
    scg.priority_rank AS goal_priority,
    scg.target_company_type,
    sk.skill_id,
    sk.skill_name,
    sk.category AS skill_category,
    rsr.required_proficiency,
    COALESCE(ss.current_proficiency, 0) AS current_proficiency,
    GREATEST(0, rsr.required_proficiency - COALESCE(ss.current_proficiency, 0)) AS skill_gap,
    rsr.importance_level,
    rsr.weight_score,
    rsr.recommended_order,
    ROUND(
        GREATEST(0, rsr.required_proficiency - COALESCE(ss.current_proficiency, 0)) * rsr.weight_score,
        2
    ) AS gap_urgency_score,
    COALESCE(ss.confidence_level, 'Unassessed') AS confidence_level,
    COALESCE(ss.assessment_source, 'None') AS assessment_source,
    ss.last_assessed_at
FROM students s
JOIN student_career_goals scg ON s.student_id = scg.student_id AND scg.status = 'Active'
JOIN career_roles cr ON scg.role_id = cr.role_id
JOIN role_skill_requirements rsr ON cr.role_id = rsr.role_id
JOIN skills sk ON rsr.skill_id = sk.skill_id
LEFT JOIN student_skills ss ON s.student_id = ss.student_id AND sk.skill_id = ss.skill_id;

-- ============================================================================
-- VIEW 2: ACTIVE ACADEMIC WORKLOAD & URGENCY
-- ============================================================================
-- Calculates countdown hours, remaining workload, and urgency classification.
CREATE OR REPLACE VIEW v_student_active_workload AS
SELECT
    at.task_id,
    at.student_id,
    at.subject,
    at.task_title,
    at.task_type,
    at.priority AS declared_priority,
    at.difficulty,
    at.estimated_duration_minutes,
    at.remaining_duration_minutes,
    at.deadline,
    at.status,
    at.completion_percentage,
    ROUND(CAST(EXTRACT(EPOCH FROM (at.deadline - CURRENT_TIMESTAMP)) / 3600.0 AS NUMERIC), 1) AS hours_until_deadline,
    ROUND(CAST(EXTRACT(EPOCH FROM (at.deadline - CURRENT_TIMESTAMP)) / 86400.0 AS NUMERIC), 1) AS days_until_deadline,
    CASE
        WHEN at.deadline < CURRENT_TIMESTAMP THEN 'OVERDUE'
        WHEN at.deadline <= CURRENT_TIMESTAMP + INTERVAL '24 hours' THEN 'CRITICAL (Due <= 24h)'
        WHEN at.deadline <= CURRENT_TIMESTAMP + INTERVAL '48 hours' THEN 'HIGH (Due <= 48h)'
        WHEN at.deadline <= CURRENT_TIMESTAMP + INTERVAL '7 days' THEN 'MEDIUM (Due This Week)'
        ELSE 'LOW (Due Later)'
    END AS deadline_urgency_category
FROM academic_tasks at
WHERE at.status NOT IN ('Completed', 'Cancelled');

-- ============================================================================
-- VIEW 3: WEEKLY PROGRESS AND CONSISTENCY SUMMARY
-- ============================================================================
CREATE OR REPLACE VIEW v_student_weekly_progress AS
SELECT
    s.student_id,
    s.full_name,
    COALESCE(SUM(pl.time_spent_minutes), 0) AS total_study_minutes_last_7d,
    ROUND(COALESCE(SUM(pl.time_spent_minutes), 0) / 60.0, 1) AS total_study_hours_last_7d,
    COALESCE(SUM(CASE WHEN pl.task_category = 'Academic' THEN pl.time_spent_minutes ELSE 0 END), 0) AS academic_minutes_last_7d,
    COALESCE(SUM(CASE WHEN pl.task_category = 'Placement' THEN pl.time_spent_minutes ELSE 0 END), 0) AS placement_minutes_last_7d,
    COALESCE(SUM(pl.problems_completed), 0) AS coding_problems_solved_last_7d,
    COUNT(DISTINCT pl.log_date) AS active_days_last_7d,
    COALESCE(stk.current_streak_days, 0) AS current_streak_days,
    COALESCE(stk.longest_streak_days, 0) AS longest_streak_days
FROM students s
LEFT JOIN progress_logs pl ON s.student_id = pl.student_id AND pl.log_date >= CURRENT_DATE - INTERVAL '7 days'
LEFT JOIN student_streaks stk ON s.student_id = stk.student_id
GROUP BY s.student_id, s.full_name, stk.current_streak_days, stk.longest_streak_days;

-- ============================================================================
-- FUNCTION: AI DAILY PLANNING CONTEXT COMPILER
-- ============================================================================
-- Returns a unified JSON document containing everything the AI model needs
-- to synthesize the daily plan: profile, availability, timetable, career goal,
-- skill gaps, academic deadlines, pending placement prep tasks, and progress.
CREATE OR REPLACE FUNCTION fn_get_ai_daily_plan_context(
    p_student_id UUID,
    p_plan_date DATE DEFAULT CURRENT_DATE
)
RETURNS JSONB AS $$
DECLARE
    v_day_name VARCHAR(20);
    v_result JSONB;
BEGIN
    v_day_name := TRIM(TO_CHAR(p_plan_date, 'Day'));

    SELECT jsonb_build_object(
        'student_profile', (
            SELECT jsonb_build_object(
                'student_id', s.student_id,
                'name', s.full_name,
                'college', s.college_name,
                'degree', s.degree,
                'branch', s.branch,
                'year', s.current_year,
                'semester', s.current_semester,
                'graduation_year', s.graduation_year,
                'preferred_daily_hours', s.preferred_study_hours_per_day,
                'default_prep_minutes', s.daily_available_prep_minutes,
                'timezone', s.timezone
            )
            FROM students s
            WHERE s.student_id = p_student_id
        ),
        'planning_target', jsonb_build_object(
            'date', p_plan_date,
            'day_of_week', v_day_name
        ),
        'today_availability', (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'start_time', sa.available_start_time,
                        'end_time', sa.available_end_time,
                        'duration_minutes', sa.available_duration_minutes,
                        'energy_level', sa.energy_level,
                        'preferred_activity', sa.preferred_activity,
                        'notes', sa.notes
                    )
                ),
                '[]'::jsonb
            )
            FROM study_availability sa
            WHERE sa.student_id = p_student_id AND sa.availability_date = p_plan_date
        ),
        'college_fixed_schedule', (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'start_time', sch.start_time,
                        'end_time', sch.end_time,
                        'activity', sch.activity_name,
                        'type', sch.activity_type,
                        'location', sch.location_or_room
                    ) ORDER BY sch.start_time
                ),
                '[]'::jsonb
            )
            FROM student_schedule sch
            WHERE sch.student_id = p_student_id AND sch.day_of_week = v_day_name
        ),
        'primary_career_goal', (
            SELECT jsonb_build_object(
                'role_title', cr.role_title,
                'target_company_type', scg.target_company_type,
                'target_date', scg.target_placement_date,
                'priority', scg.priority_rank
            )
            FROM student_career_goals scg
            JOIN career_roles cr ON scg.role_id = cr.role_id
            WHERE scg.student_id = p_student_id AND scg.priority_rank = 1 AND scg.status = 'Active'
            LIMIT 1
        ),
        'priority_skill_gaps', (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'skill_name', vsg.skill_name,
                        'category', vsg.skill_category,
                        'required_level', vsg.required_proficiency,
                        'current_level', vsg.current_proficiency,
                        'gap', vsg.skill_gap,
                        'importance', vsg.importance_level,
                        'urgency_score', vsg.gap_urgency_score
                    ) ORDER BY vsg.gap_urgency_score DESC
                ),
                '[]'::jsonb
            )
            FROM v_student_skill_gaps vsg
            WHERE vsg.student_id = p_student_id AND vsg.skill_gap > 0
        ),
        'urgent_academic_workload', (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'task_id', vaw.task_id,
                        'subject', vaw.subject,
                        'title', vaw.task_title,
                        'type', vaw.task_type,
                        'deadline', vaw.deadline,
                        'hours_remaining', vaw.hours_until_deadline,
                        'remaining_minutes', vaw.remaining_duration_minutes,
                        'urgency_category', vaw.deadline_urgency_category,
                        'status', vaw.status
                    ) ORDER BY vaw.deadline ASC
                ),
                '[]'::jsonb
            )
            FROM v_student_active_workload vaw
            WHERE vaw.student_id = p_student_id
        ),
        'incomplete_placement_tasks', (
            SELECT COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'task_id', lt.task_id,
                        'skill_name', sk.skill_name,
                        'title', lt.title,
                        'estimated_minutes', lt.estimated_duration_minutes,
                        'remaining_minutes', lt.remaining_duration_minutes,
                        'difficulty', lt.difficulty,
                        'priority', lt.priority,
                        'status', lt.status
                    ) ORDER BY lt.priority DESC, lt.created_at ASC
                ),
                '[]'::jsonb
            )
            FROM learning_tasks lt
            JOIN skills sk ON lt.skill_id = sk.skill_id
            WHERE lt.student_id = p_student_id AND lt.status NOT IN ('Completed', 'Cancelled')
        ),
        'recent_progress_summary', (
            SELECT jsonb_build_object(
                'study_hours_last_7d', vwp.total_study_hours_last_7d,
                'academic_minutes_last_7d', vwp.academic_minutes_last_7d,
                'placement_minutes_last_7d', vwp.placement_minutes_last_7d,
                'problems_solved_last_7d', vwp.coding_problems_solved_last_7d,
                'current_streak_days', vwp.current_streak_days
            )
            FROM v_student_weekly_progress vwp
            WHERE vwp.student_id = p_student_id
        )
    ) INTO v_result;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;


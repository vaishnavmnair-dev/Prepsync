-- ============================================================================
-- PROJECT: BRIDGING THE GAP BETWEEN COLLEGE WORK AND PLACEMENT PREPARATION
-- SCRIPT 04: EXAMPLE SQL QUERIES (12 PRODUCT FLOW QUERIES)
-- ============================================================================
-- Description: The 12 essential operational queries answering the product requirements.
-- Demo Student ID: '11111111-1111-1111-1111-111111111111'
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: GET STUDENT'S CAREER GOAL
-- Retrieves student's active career goals, target companies, and target dates.
-- ----------------------------------------------------------------------------
SELECT
    s.student_id,
    s.full_name,
    cr.role_title AS career_goal,
    scg.target_company_type,
    scg.target_placement_date,
    scg.priority_rank,
    scg.status AS goal_status
FROM student_career_goals scg
JOIN career_roles cr ON scg.role_id = cr.role_id
JOIN students s ON scg.student_id = s.student_id
WHERE scg.student_id = '11111111-1111-1111-1111-111111111111'
  AND scg.status = 'Active'
ORDER BY scg.priority_rank ASC;

-- ----------------------------------------------------------------------------
-- QUERY 2: GET REQUIRED SKILLS FOR THE CAREER
-- Fetches curriculum skills required for 'Software Developer' with weights & order.
-- ----------------------------------------------------------------------------
SELECT
    cr.role_title,
    sk.skill_name,
    sk.category,
    rsr.required_proficiency,
    CASE rsr.required_proficiency
        WHEN 0 THEN '0 - Not Started'
        WHEN 1 THEN '1 - Beginner'
        WHEN 2 THEN '2 - Basic'
        WHEN 3 THEN '3 - Intermediate'
        WHEN 4 THEN '4 - Advanced'
        WHEN 5 THEN '5 - Expert'
    END AS required_level_label,
    rsr.importance_level,
    rsr.weight_score,
    rsr.recommended_order
FROM role_skill_requirements rsr
JOIN career_roles cr ON rsr.role_id = cr.role_id
JOIN skills sk ON rsr.skill_id = sk.skill_id
WHERE cr.role_title = 'Software Developer'
ORDER BY rsr.recommended_order ASC;

-- ----------------------------------------------------------------------------
-- QUERY 3: CALCULATE SKILL GAPS
-- Compares required career proficiency with student's current assessed level.
-- ----------------------------------------------------------------------------
SELECT
    vsg.skill_name,
    vsg.skill_category,
    vsg.required_proficiency AS required_level,
    vsg.current_proficiency AS student_level,
    vsg.skill_gap,
    vsg.importance_level,
    vsg.gap_urgency_score,
    vsg.confidence_level,
    vsg.assessment_source
FROM v_student_skill_gaps vsg
WHERE vsg.student_id = '11111111-1111-1111-1111-111111111111'
ORDER BY vsg.gap_urgency_score DESC;

-- ----------------------------------------------------------------------------
-- QUERY 4: GET UPCOMING ACADEMIC DEADLINES
-- Lists all active college tasks sorted by nearest deadline with countdown hours.
-- ----------------------------------------------------------------------------
SELECT
    at.task_id,
    at.subject,
    at.task_title,
    at.task_type,
    at.priority,
    at.deadline,
    ROUND(CAST(EXTRACT(EPOCH FROM (at.deadline - CURRENT_TIMESTAMP)) / 3600.0 AS NUMERIC), 1) AS hours_remaining,
    at.remaining_duration_minutes,
    at.status
FROM academic_tasks at
WHERE at.student_id = '11111111-1111-1111-1111-111111111111'
  AND at.deadline >= CURRENT_TIMESTAMP
  AND at.status NOT IN ('Completed', 'Cancelled')
ORDER BY at.deadline ASC;

-- ----------------------------------------------------------------------------
-- QUERY 5: GET OVERDUE TASKS
-- Detects tasks that missed their deadline and are still not completed.
-- ----------------------------------------------------------------------------
SELECT
    at.task_id,
    at.subject,
    at.task_title,
    at.task_type,
    at.deadline,
    ROUND(CAST(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - at.deadline)) / 3600.0 AS NUMERIC), 1) AS hours_overdue,
    at.remaining_duration_minutes,
    at.priority,
    at.status
FROM academic_tasks at
WHERE at.student_id = '11111111-1111-1111-1111-111111111111'
  AND at.deadline < CURRENT_TIMESTAMP
  AND at.status NOT IN ('Completed', 'Cancelled')
ORDER BY at.deadline ASC;

-- ----------------------------------------------------------------------------
-- QUERY 6: GET TODAY'S AVAILABLE STUDY TIME
-- Retrieves available time windows, duration, and energy level for the student.
-- ----------------------------------------------------------------------------
SELECT
    sa.availability_date,
    sa.available_start_time,
    sa.available_end_time,
    sa.available_duration_minutes,
    ROUND(sa.available_duration_minutes / 60.0, 1) AS available_hours,
    sa.energy_level,
    sa.preferred_activity,
    sa.notes
FROM study_availability sa
WHERE sa.student_id = '11111111-1111-1111-1111-111111111111'
  AND sa.availability_date = CURRENT_DATE;

-- ----------------------------------------------------------------------------
-- QUERY 7: GET INCOMPLETE PLACEMENT TASKS
-- Fetches pending learning tasks linked to career skills, sorted by priority.
-- ----------------------------------------------------------------------------
SELECT
    lt.task_id,
    sk.skill_name,
    sk.category,
    lt.title AS task_title,
    lt.difficulty,
    lt.priority,
    lt.estimated_duration_minutes,
    lt.remaining_duration_minutes,
    lt.completion_percentage,
    lt.status
FROM learning_tasks lt
JOIN skills sk ON lt.skill_id = sk.skill_id
WHERE lt.student_id = '11111111-1111-1111-1111-111111111111'
  AND lt.status NOT IN ('Completed', 'Cancelled')
ORDER BY lt.priority DESC, lt.estimated_duration_minutes ASC;

-- ----------------------------------------------------------------------------
-- QUERY 8: GET THE STUDENT'S CURRENT WORKLOAD (COMBINED TOTALS)
-- Summarizes total academic workload vs placement preparation workload.
-- ----------------------------------------------------------------------------
SELECT
    s.student_id,
    s.full_name,
    COUNT(DISTINCT at.task_id) AS active_academic_task_count,
    COALESCE(SUM(at.remaining_duration_minutes), 0) AS total_academic_remaining_minutes,
    ROUND(COALESCE(SUM(at.remaining_duration_minutes), 0) / 60.0, 1) AS total_academic_remaining_hours,
    COUNT(DISTINCT lt.task_id) AS pending_placement_task_count,
    COALESCE(SUM(lt.remaining_duration_minutes), 0) AS total_placement_remaining_minutes,
    ROUND(COALESCE(SUM(lt.remaining_duration_minutes), 0) / 60.0, 1) AS total_placement_remaining_hours,
    (COALESCE(SUM(at.remaining_duration_minutes), 0) + COALESCE(SUM(lt.remaining_duration_minutes), 0)) AS total_workload_minutes
FROM students s
LEFT JOIN academic_tasks at ON s.student_id = at.student_id AND at.status NOT IN ('Completed', 'Cancelled')
LEFT JOIN learning_tasks lt ON s.student_id = lt.student_id AND lt.status NOT IN ('Completed', 'Cancelled')
WHERE s.student_id = '11111111-1111-1111-1111-111111111111'
GROUP BY s.student_id, s.full_name;

-- ----------------------------------------------------------------------------
-- QUERY 9: GET TODAY'S PLANNED TASKS
-- Retrieves student's active schedule for today including AI reasoning for each item.
-- ----------------------------------------------------------------------------
SELECT
    dp.plan_date,
    dpi.item_order,
    dpi.task_category,
    dpi.custom_title,
    dpi.scheduled_start_time,
    dpi.scheduled_end_time,
    dpi.planned_duration_minutes,
    dpi.priority_score,
    dpi.status AS item_status,
    dpi.ai_item_reasoning
FROM daily_plans dp
JOIN daily_plan_items dpi ON dp.plan_id = dpi.plan_id
WHERE dp.student_id = '11111111-1111-1111-1111-111111111111'
  AND dp.plan_date = CURRENT_DATE
ORDER BY dpi.item_order ASC;

-- ----------------------------------------------------------------------------
-- QUERY 10: GET COMPLETED TASKS (ACROSS BOTH WORKLOADS)
-- Retrieves recently completed academic assignments and placement tasks.
-- ----------------------------------------------------------------------------
SELECT
    'Academic' AS category,
    at.subject || ': ' || at.task_title AS title,
    at.estimated_duration_minutes AS duration_minutes,
    at.completed_at
FROM academic_tasks at
WHERE at.student_id = '11111111-1111-1111-1111-111111111111'
  AND at.status = 'Completed'

UNION ALL

SELECT
    'Placement' AS category,
    sk.skill_name || ': ' || lt.title AS title,
    lt.estimated_duration_minutes AS duration_minutes,
    lt.completed_at
FROM learning_tasks lt
JOIN skills sk ON lt.skill_id = sk.skill_id
WHERE lt.student_id = '11111111-1111-1111-1111-111111111111'
  AND lt.status = 'Completed'
ORDER BY completed_at DESC NULLS LAST;

-- ----------------------------------------------------------------------------
-- QUERY 11: GET RECENT PROGRESS (PAST 7 DAYS ACTIVITY LOG)
-- Detailed log of study sessions, time spent, and skill proficiency upgrades.
-- ----------------------------------------------------------------------------
SELECT
    pl.log_date,
    pl.task_category,
    COALESCE(sk.skill_name, 'General') AS skill_name,
    pl.time_spent_minutes,
    pl.problems_completed,
    pl.previous_proficiency,
    pl.new_proficiency,
    pl.notes
FROM progress_logs pl
LEFT JOIN skills sk ON pl.skill_id = sk.skill_id
WHERE pl.student_id = '11111111-1111-1111-1111-111111111111'
  AND pl.log_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY pl.log_date DESC, pl.created_at DESC;

-- ----------------------------------------------------------------------------
-- QUERY 12: GET SKILLS WITH THE LARGEST GAPS
-- Pinpoints where the student needs the most growth relative to target role.
-- ----------------------------------------------------------------------------
SELECT
    vsg.skill_name,
    vsg.skill_category,
    vsg.current_proficiency,
    vsg.required_proficiency,
    vsg.skill_gap,
    vsg.importance_level,
    vsg.weight_score,
    vsg.gap_urgency_score
FROM v_student_skill_gaps vsg
WHERE vsg.student_id = '11111111-1111-1111-1111-111111111111'
  AND vsg.skill_gap > 0
ORDER BY vsg.skill_gap DESC, vsg.gap_urgency_score DESC;


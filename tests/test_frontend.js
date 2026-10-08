/**
 * Automated Test Suite for AdaptiveStudy AI Frontend
 * Run with: node tests/test_frontend.js
 */

const fs = require('fs');
const path = require('path');
const {
  DEFAULT_USER,
  DEFAULT_TASKS,
  STUDY_TRACKS,
  formatMinutesToTime,
  calculateSchedule,
  parseNaturalLanguageTasks,
  generateMicroSteps
} = require('../Frontend/app.js');

let passedTests = 0;
let failedTests = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`  ✓ PASS: ${testName}`);
    passedTests++;
  } else {
    console.error(`  ✗ FAIL: ${testName}`);
    failedTests++;
  }
}

function assertEqual(actual, expected, testName) {
  if (actual === expected) {
    console.log(`  ✓ PASS: ${testName}`);
    passedTests++;
  } else {
    console.error(`  ✗ FAIL: ${testName} (Expected: ${expected}, Got: ${actual})`);
    failedTests++;
  }
}

console.log('====================================================');
console.log(' RUNNING ADAPTIVESTUDY AI FRONTEND TEST SUITE');
console.log('====================================================\n');

// -----------------------------------------------------------------
// 1. Time Formatting Tests
// -----------------------------------------------------------------
console.log('1. Testing Time Formatting (formatMinutesToTime)...');
assertEqual(formatMinutesToTime(0), '12:00 AM', '0 mins -> 12:00 AM');
assertEqual(formatMinutesToTime(60), '1:00 AM', '60 mins -> 1:00 AM');
assertEqual(formatMinutesToTime(720), '12:00 PM', '720 mins -> 12:00 PM');
assertEqual(formatMinutesToTime(1080), '6:00 PM', '1080 mins -> 6:00 PM (Start Time)');
assertEqual(formatMinutesToTime(1380), '11:00 PM', '1380 mins -> 11:00 PM (End Time)');
assertEqual(formatMinutesToTime(1440), '12:00 AM', '1440 mins -> 12:00 AM (Midnight rollover)');
assertEqual(formatMinutesToTime(1500), '1:00 AM', '1500 mins -> 1:00 AM (Post-midnight)');

// -----------------------------------------------------------------
// 2. Schedule Engine & Break Injection Tests
// -----------------------------------------------------------------
console.log('\n2. Testing Schedule Calculation Engine...');

const mockState = {
  studyWindow: { start: '18:00', end: '23:00' },
  lateOffset: 0,
  tasks: [
    { id: 't1', title: 'Task Light', type: 'light', durationMin: 20, completed: false, subject: 'Review' },
    { id: 't2', title: 'Task Hard', type: 'hard', durationMin: 50, completed: false, subject: 'Coding' },
    { id: 't3', title: 'Task Med', type: 'medium', durationMin: 35, completed: false, subject: 'Lab' },
    { id: 't4', title: 'Task Done', type: 'hard', durationMin: 40, completed: true, subject: 'Done' }
  ]
};

const result = calculateSchedule(mockState);

assertEqual(result.budget, 300, 'Total study window budget is 300 minutes (5 hours)');
assertEqual(result.startFormatted, '6:00 PM', 'Start time formatted correctly');
assertEqual(result.endFormatted, '11:00 PM', 'End time formatted correctly');

// Check priority order: uncompleted Hard first, then Med, then Light, then Done
const nonBreakSlots = result.timeline.filter(s => !s.isBreak);
assertEqual(nonBreakSlots[0].taskId, 't2', 'Hard uncompleted task is scheduled first');
assertEqual(nonBreakSlots[1].taskId, 't3', 'Medium uncompleted task is scheduled second');
assertEqual(nonBreakSlots[2].taskId, 't1', 'Light uncompleted task is scheduled third');
assertEqual(nonBreakSlots[3].taskId, 't4', 'Completed task is placed last');

// Test Break Insertion:
// Task 2 is 50m. Task 3 is 35m.
// continuousWorkTime after Task 2: 50m
// In next iteration, continuousWorkTime was 50 < 60, so Task 3 scheduled (currentClock = start + 50 + 35 = 85m).
// In iteration after Task 3, continuousWorkTime is 85 >= 60 -> Break MUST be inserted!
const breakSlots = result.timeline.filter(s => s.isBreak);
assert(breakSlots.length >= 1, 'Automatic 15-minute refresh break was inserted');
assertEqual(breakSlots[0].duration, 15, 'Break duration is exactly 15 minutes');

// -----------------------------------------------------------------
// 3. Late Offset Resilience Tests
// -----------------------------------------------------------------
console.log('\n3. Testing Late Offset Dynamic Rescheduling...');
const lateState = {
  ...mockState,
  lateOffset: 20
};
const lateResult = calculateSchedule(lateState);
assertEqual(lateResult.timeline[0].start, '6:20 PM', 'First task start time shifted by +20 minutes to 6:20 PM');

// -----------------------------------------------------------------
// 4. Overload Protection & Overflow Marking
// -----------------------------------------------------------------
console.log('\n4. Testing Burnout Prevention Overtime Safeguard...');
const heavyState = {
  studyWindow: { start: '18:00', end: '20:00' }, // 2 hours = 120 mins
  lateOffset: 0,
  tasks: [
    { id: 'h1', title: 'Mega Coding', type: 'hard', durationMin: 60, completed: false, subject: 'DSA' },
    { id: 'h2', title: 'Big Lab', type: 'medium', durationMin: 50, completed: false, subject: 'Lab' },
    { id: 'h3', title: 'Huge Reading', type: 'medium', durationMin: 45, completed: false, subject: 'Theory' }
  ]
};
const heavyResult = calculateSchedule(heavyState);
assert(heavyResult.isExceeded, 'Identifies schedule exceeds study window');
const lastTaskSlot = heavyResult.timeline.find(s => s.taskId === 'h3');
assert(lastTaskSlot.isOverTime, 'Tasks beyond time window are marked as isOverTime=true');
assertEqual(lastTaskSlot.tag, 'Shifted to Tomorrow', 'Overflowing tasks are labeled "Shifted to Tomorrow"');

// -----------------------------------------------------------------
// 5. NLP Natural Language Task Extractor Tests
// -----------------------------------------------------------------
console.log('\n5. Testing NLP Task Extractor...');
const sampleNotes = 'Finish 2 C programs on pointers, submit Chemistry lab record, read 10 slides of DBMS, solve 3 calculus integrals';
const extracted = parseNaturalLanguageTasks(sampleNotes);

assertEqual(extracted.length, 4, 'Extracted 4 individual tasks from messy notes');
assertEqual(extracted[0].type, 'hard', 'C pointers detected as hard');
assertEqual(extracted[0].subject, 'Data Structures', 'C pointers subject detected as Data Structures');

assertEqual(extracted[1].type, 'medium', 'Lab record detected as medium');
assertEqual(extracted[1].subject, 'Applied Sciences', 'Lab record subject detected as Applied Sciences');

assertEqual(extracted[2].type, 'light', 'Reading slides detected as light');
assertEqual(extracted[2].subject, 'Database Systems', 'DBMS subject detected as Database Systems');

assertEqual(extracted[3].type, 'hard', 'Calculus integrals detected as hard');
assertEqual(extracted[3].subject, 'Mathematics', 'Calculus subject detected as Mathematics');

// -----------------------------------------------------------------
// 6. Micro-Steps AI Task Breakdown Tests
// -----------------------------------------------------------------
console.log('\n6. Testing 5-Minute Micro-Steps AI Breakdown...');
const hardBreakdown = generateMicroSteps({ title: 'C++ Pointers', type: 'hard' });
assert(hardBreakdown.kickstart.length > 10, 'Hard task kickstart prompt is present');
assert(hardBreakdown.steps.length >= 3, 'Generates at least 3 actionable micro-steps for hard task');

const medBreakdown = generateMicroSteps({ title: 'Physics Record', type: 'medium' });
assert(medBreakdown.kickstart.includes('record') || medBreakdown.kickstart.includes('PDF') || medBreakdown.kickstart.includes('notebook'), 'Medium task has lab-focused starter tip');
assert(medBreakdown.steps.length >= 3, 'Generates at least 3 actionable micro-steps for medium task');

const lightBreakdown = generateMicroSteps({ title: 'DBMS Slides', type: 'light' });
assert(lightBreakdown.kickstart.includes('slide'), 'Light task has slide-focused starter tip');
assert(lightBreakdown.steps.length >= 3, 'Generates at least 3 actionable micro-steps for light task');

// -----------------------------------------------------------------
// 7. HTML Markup & Element ID Verification Tests
// -----------------------------------------------------------------
console.log('\n7. Testing Frontend HTML Markup Integrity & DOM IDs...');
const htmlPath = path.join(__dirname, '../Frontend/index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

const requiredIds = [
  'desktopDockContainer',
  'dock-home',
  'dock-hub',
  'dock-timeline',
  'dock-performance',
  'dock-profile',
  'dockTaskBadge',
  'deviceFrameWrapper',
  'phoneTopBar',
  'phoneClock',
  'phoneBottomBar',
  'toggleMobileFrameBtn',
  'frameIcon',
  'frameLabel',
  'tab-home-view',
  'tab-hub-view',
  'tab-timeline-view',
  'tab-performance-view',
  'tab-profile-view',
  'timerDisplay',
  'toggleTimerBtn',
  'resetTimerBtn',
  'homeTaskListPreview',
  'homeWelcomeHeading',
  'homeStreakBadge',
  'homeWindowBadge',
  'inputStartTime',
  'inputEndTime',
  'windowTotalHoursBadge',
  'hubWindowDisplayStart',
  'hubWindowDisplayEnd',
  'metricHardCount',
  'metricMediumCount',
  'metricCompletedCount',
  'metricDeferredCount',
  'taskInputForm',
  'quickTaskText',
  'typeBtn-hard',
  'typeBtn-medium',
  'typeBtn-light',
  'aiAutoExtractBtn',
  'generateScheduleBtn',
  'queueHeader',
  'taskQueueList',
  'weekDaysStrip',
  'timelineDateHeader',
  'aiAdviceBanner',
  'aiAdviceText',
  'lateOffsetStatus',
  'lateOffsetBtn',
  'timelineSlotsContainer',
  'profileAuthActionSlot',
  'profileMainContent',
  'authModal',
  'authForm',
  'authEmailInput',
  'authPasswordInput',
  'authSubmitBtn',
  'authDemoBtn',
  'breakdownModal',
  'breakdownModalTaskTitle',
  'breakdownModalTaskMeta',
  'breakdownLoadingState',
  'breakdownContentArea',
  'breakdownKickstartText',
  'breakdownStepsList',
  'toastNotification',
  'toastMessage'
];

requiredIds.forEach(id => {
  const exists = htmlContent.includes(`id="${id}"`);
  assert(exists, `HTML contains element with id="${id}"`);
});

// Check critical function bindings
const requiredFunctions = [
  'setTab(',
  'toggleTaskDone(',
  'deleteTask(',
  'setQuickType(',
  'updateStudyWindow(',
  'toggleMobileFrame(',
  'toggleTimer(',
  'resetTimer(',
  'handleLateOffset(',
  'selectDay(',
  'dismissAiAdvice(',
  'handleAddTaskSubmit(',
  'handleAiAutoExtract(',
  'handleGenerateSchedule(',
  'handleBreakdownTask(',
  'closeBreakdownModal(',
  'selectTrack(',
  'saveProfile(',
  'openAuthModal(',
  'closeAuthModal(',
  'handleAuthSubmit(',
  'handleDemoLogin(',
  'handleLogout('
];

requiredFunctions.forEach(fn => {
  const exists = htmlContent.includes(fn);
  assert(exists, `HTML / Script binds function "${fn}"`);
});

console.log('\n====================================================');
console.log(` RESULTS: ${passedTests} PASSED, ${failedTests} FAILED`);
console.log('====================================================\n');

if (failedTests > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL FRONTEND TESTS PASSED SUCCESSFULLY!\n');
  process.exit(0);
}


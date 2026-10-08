/**
 * Automated Verification Test for Task Breakdown Engine:
 * - Accurate dynamic task deconstruction
 * - Progress tracking & step checklist
 * - Queue splitting into micro-subtasks
 *
 * Run with: node tests/test_breakdown.js
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

let passedTests = 0;
let failedTests = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  ✓ PASS: ${message}`);
    passedTests++;
  } else {
    console.error(`  ✗ FAIL: ${message}`);
    failedTests++;
  }
}

function assertEqual(actual, expected, message) {
  if (actual === expected) {
    console.log(`  ✓ PASS: ${message}`);
    passedTests++;
  } else {
    console.error(`  ✗ FAIL: ${message} (Expected: ${expected}, Got: ${actual})`);
    failedTests++;
  }
}

console.log('====================================================');
console.log(' RUNNING TASK BREAKDOWN ENGINE TESTS');
console.log('====================================================\n');

// 1. Mock Environment
const domElements = {};
function createMockElement(id) {
  return {
    id,
    innerText: '',
    innerHTML: '',
    value: '',
    className: '',
    style: {},
    classList: {
      add: function(c) { this._classes = (this._classes || []).concat(c); },
      remove: function(c) { this._classes = (this._classes || []).filter(x => x !== c); },
      contains: function(c) { return (this._classes || []).includes(c); }
    },
    setAttribute: () => {},
    getAttribute: () => null,
    addEventListener: () => {},
    removeEventListener: () => {}
  };
}

const mockDocument = {
  getElementById: (id) => {
    if (!domElements[id]) domElements[id] = createMockElement(id);
    return domElements[id];
  },
  querySelectorAll: (selector) => {
    if (selector.includes('checkbox')) {
      return domElements['_checkboxes'] || [];
    }
    return [];
  },
  addEventListener: () => {},
  removeEventListener: () => {}
};

const mockStorage = {};
const localStorage = {
  getItem: (key) => (key in mockStorage ? mockStorage[key] : null),
  setItem: (key, val) => { mockStorage[key] = String(val); },
  removeItem: (key) => { delete mockStorage[key]; }
};

const sandbox = {
  console,
  setTimeout: (fn) => fn(),
  clearTimeout: () => {},
  setInterval: () => {},
  clearInterval: () => {},
  localStorage,
  document: mockDocument,
  window: {
    AudioContext: null,
    lucide: { createIcons: () => {} },
    addEventListener: () => {},
    removeEventListener: () => {}
  },
  fetch: () => Promise.reject(new Error('offline')),
  showToast: () => {},
  closeAuthModal: () => {}
};
sandbox.window.document = mockDocument;
sandbox.window.localStorage = localStorage;

const htmlPath = path.join(__dirname, '../Frontend/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
  console.error('No script found');
  process.exit(1);
}

vm.createContext(sandbox);
vm.runInContext(
  scriptMatch[1] +
  '\nthis.STATE = STATE;' +
  'this.generateMicroSteps = generateMicroSteps;' +
  'this.handleBreakdownTask = handleBreakdownTask;' +
  'this.closeBreakdownModal = closeBreakdownModal;' +
  'this.splitTaskIntoMicroSteps = splitTaskIntoMicroSteps;' +
  'this.handleStepCheckboxToggle = handleStepCheckboxToggle;' +
  'this.persistState = persistState;' +
  'this.renderAllViews = renderAllViews;',
  sandbox
);

const {
  STATE,
  generateMicroSteps,
  handleBreakdownTask,
  closeBreakdownModal,
  splitTaskIntoMicroSteps,
  handleStepCheckboxToggle
} = sandbox;

// -----------------------------------------------------------------
// Test 1: Task-Aware Breakdown Logic
// -----------------------------------------------------------------
console.log('1. Testing Task-Specific AI Deconstruction...');

const codingTask = { title: 'Finish 2 C programs on pointers', subject: 'Data Structures', type: 'hard', durationMin: 45 };
const codingBd = generateMicroSteps(codingTask);
assert(codingBd.kickstart.includes('editor') || codingBd.kickstart.includes('boilerplate'), 'Coding kickstart mentions editor/boilerplate');
assert(codingBd.steps.length >= 3, 'Coding task has >= 3 actionable steps');
assert(codingBd.steps.some(s => s.toLowerCase().includes('core logic') || s.toLowerCase().includes('pointers')), 'Coding step mentions core logic/pointers');

const labTask = { title: 'Submit Chemistry lab record', subject: 'Applied Sciences', type: 'medium', durationMin: 35 };
const labBd = generateMicroSteps(labTask);
assert(labBd.kickstart.includes('record') || labBd.kickstart.includes('PDF') || labBd.kickstart.includes('notebook'), 'Lab kickstart mentions record notebook/PDF');
assert(labBd.steps.some(s => s.toLowerCase().includes('aim') || s.toLowerCase().includes('formula')), 'Lab step mentions Aim/formula');
assert(labBd.steps.some(s => s.toLowerCase().includes('observation') || s.toLowerCase().includes('error')), 'Lab step mentions observations/error');

const readingTask = { title: 'Read 10 slides of DBMS', subject: 'Database Systems', type: 'light', durationMin: 20 };
const readingBd = generateMicroSteps(readingTask);
assert(readingBd.kickstart.includes('slide'), 'Reading kickstart mentions slides');
assert(readingBd.steps.some(s => s.toLowerCase().includes('slides') || s.toLowerCase().includes('concepts')), 'Reading step mentions slides/concepts');

const mathTask = { title: 'Solve 3 calculus integrals', subject: 'Mathematics', type: 'hard', durationMin: 40 };
const mathBd = generateMicroSteps(mathTask);
assert(mathBd.kickstart.includes('math') || mathBd.kickstart.includes('formula'), 'Math kickstart mentions formula/math');
assert(mathBd.steps.some(s => s.toLowerCase().includes('integral') || s.toLowerCase().includes('algebraic') || s.toLowerCase().includes('standard form')), 'Math step mentions integration/standard forms');

// -----------------------------------------------------------------
// Test 2: Modal Opening & Rendering
// -----------------------------------------------------------------
console.log('\n2. Testing Modal Opening for Task...');

STATE.tasks = [
  { id: 'task-test-1', title: 'Submit Chemistry lab record', subject: 'Applied Sciences', type: 'medium', durationMin: 35, completed: false }
];

handleBreakdownTask('task-test-1');

const titleEl = mockDocument.getElementById('breakdownModalTaskTitle');
assertEqual(titleEl.innerText, 'Submit Chemistry lab record', 'Modal task title set to task name');

const kickstartEl = mockDocument.getElementById('breakdownKickstartText');
assert(kickstartEl.innerText.length > 10, 'Kickstart tip is populated');

const stepsListEl = mockDocument.getElementById('breakdownStepsList');
assert(stepsListEl.innerHTML.includes('Step 1'), 'Steps list includes Step 1');
assert(stepsListEl.innerHTML.includes('Step 2'), 'Steps list includes Step 2');
assert(stepsListEl.innerHTML.includes('mins'), 'Steps include duration badges');

// -----------------------------------------------------------------
// Test 3: Step Checkbox Progress
// -----------------------------------------------------------------
console.log('\n3. Testing Step Checkbox Progress...');

const mockCheckboxes = [
  { checked: false, parentElement: { querySelector: () => createMockElement('p1') } },
  { checked: false, parentElement: { querySelector: () => createMockElement('p2') } },
  { checked: false, parentElement: { querySelector: () => createMockElement('p3') } },
  { checked: false, parentElement: { querySelector: () => createMockElement('p4') } }
];
domElements['_checkboxes'] = mockCheckboxes;

// Check step 1
mockCheckboxes[0].checked = true;
handleStepCheckboxToggle(mockCheckboxes[0]);

const badgeEl = mockDocument.getElementById('breakdownProgressBadge');
assert(badgeEl.innerText.includes('1 of 4 completed (25%)'), 'Badge updates to 1 of 4 (25%)');

// Check all remaining steps
mockCheckboxes[1].checked = true;
mockCheckboxes[2].checked = true;
mockCheckboxes[3].checked = true;
handleStepCheckboxToggle(mockCheckboxes[3]);

assert(badgeEl.innerText.includes('4 of 4 completed (100%)'), 'Badge updates to 4 of 4 (100%)');
assert(STATE.tasks[0].completed === true, 'Parent task automatically marked completed when all micro-steps checked');

// -----------------------------------------------------------------
// Test 4: Split Task Into Micro-Steps in Queue
// -----------------------------------------------------------------
console.log('\n4. Testing Splitting Task into Queue Micro-Steps...');

STATE.tasks = [
  { id: 'task-big-code', title: 'Finish 2 C programs on pointers', subject: 'Data Structures', type: 'hard', durationMin: 45, completed: false }
];

handleBreakdownTask('task-big-code');
assertEqual(STATE.tasks.length, 1, 'Initially 1 big task in queue');

// Execute split
splitTaskIntoMicroSteps();

assert(STATE.tasks.length >= 3, `Big task successfully split into ${STATE.tasks.length} micro-subtasks in queue`);
assert(!STATE.tasks.some(t => t.id === 'task-big-code'), 'Original parent task replaced in queue');
assert(STATE.tasks[0].title.includes('Step 1'), 'First subtask is labeled Step 1');
assert(STATE.tasks[0].durationMin <= 20, 'Micro-step has bite-sized duration');
assertEqual(STATE.tasks[0].subject, 'Data Structures', 'Subtasks preserve original subject');

console.log('\n====================================================');
console.log(` RESULTS: ${passedTests} PASSED, ${failedTests} FAILED`);
console.log('====================================================\n');

if (failedTests > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL TASK BREAKDOWN TESTS PASSED!\n');
  process.exit(0);
}

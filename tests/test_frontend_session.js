/**
 * Automated Test Suite for User Session Lifecycle:
 * Logout (data hidden & stored) -> Login (data restored).
 *
 * Run with: node tests/test_frontend_session.js
 */

const fs = require('fs');
const path = require('path');

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
console.log(' RUNNING LOGOUT & RE-LOGIN DATA PERSISTENCE TESTS');
console.log('====================================================\n');

// 1. Mock Browser Environment
const mockStorage = {};
const localStorage = {
  getItem: (key) => (key in mockStorage ? mockStorage[key] : null),
  setItem: (key, val) => { mockStorage[key] = String(val); },
  removeItem: (key) => { delete mockStorage[key]; },
  clear: () => { Object.keys(mockStorage).forEach(k => delete mockStorage[k]); }
};

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
      add: () => {},
      remove: () => {},
      contains: () => false
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
  querySelectorAll: () => [],
  addEventListener: () => {},
  removeEventListener: () => {}
};

// Global mocks
global.localStorage = localStorage;
global.document = mockDocument;
global.window = {
  AudioContext: null,
  lucide: { createIcons: () => {} },
  addEventListener: () => {},
  removeEventListener: () => {}
};
global.fetch = () => Promise.reject(new Error('Network offline in unit test'));
global.showToast = (msg) => {};
global.closeAuthModal = () => {};

const vm = require('vm');

// Read HTML script
const htmlPath = path.join(__dirname, '../Frontend/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// Extract JS from <script> tag
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
  console.error('Could not find <script> in index.html');
  process.exit(1);
}

// -----------------------------------------------------------------
// Test 1: Verify Initial Clean State
// -----------------------------------------------------------------
console.log('1. Testing Fresh Session (Logged Out / Guest Mode)...');

// Execute script in mock vm context
const sandbox = {
  console,
  setTimeout: () => {},
  clearTimeout: () => {},
  setInterval: () => {},
  clearInterval: () => {},
  localStorage,
  document: mockDocument,
  window: global.window,
  fetch: global.fetch,
  showToast: global.showToast,
  closeAuthModal: global.closeAuthModal
};
sandbox.window.document = mockDocument;
sandbox.window.localStorage = localStorage;

const scriptCode = scriptMatch[1]
  .replace(/const STATE =/g, 'var STATE =')
  .replace(/function /g, 'var ');

vm.createContext(sandbox);
vm.runInContext(scriptMatch[1] + '\nthis.STATE = STATE; this.handleDemoLogin = handleDemoLogin; this.handleLogout = handleLogout; this.handleAuthSubmit = handleAuthSubmit; this.persistState = persistState; this.renderAllViews = renderAllViews;', sandbox);

const { STATE, handleDemoLogin, handleLogout, handleAuthSubmit, persistState, renderAllViews } = sandbox;

assert(STATE.user === null, 'Initial user is null when unauthenticated');
assert(STATE.token === null, 'Initial token is null');
assert(Array.isArray(STATE.tasks) && STATE.tasks.length === 0, 'Initial tasks queue is empty (0 tasks)');
assertEqual(STATE.streak, 0, 'Initial streak is 0 in guest mode');

// -----------------------------------------------------------------
// Test 2: Simulate Login & Add Personal Tasks
// -----------------------------------------------------------------
console.log('\n2. Testing User Login & Data Addition...');

// Simulate Demo Login in offline / cached mode
handleDemoLogin();

assert(STATE.user !== null, 'User is logged in after handleDemoLogin()');
assertEqual(STATE.user.email, 'demo@preppilot.com', 'User email is demo@preppilot.com');
assert(STATE.token !== null, 'Session token is set');

// Add 2 tasks to this user's queue
STATE.tasks.push(
  { id: 'task-101', title: 'DSA Trees Practice', subject: 'Computer Science', type: 'hard', durationMin: 45, completed: false },
  { id: 'task-102', title: 'OS Deadlock Notes', subject: 'Operating Systems', type: 'medium', durationMin: 30, completed: true }
);
STATE.streak = 15;
persistState();
renderAllViews();

assertEqual(STATE.tasks.length, 2, 'User has 2 tasks active in queue');
assertEqual(STATE.streak, 15, 'User streak is 15');
assertEqual(mockDocument.getElementById('dockTaskBadge').innerText, 2, 'Dock task badge shows 2');
assert(mockDocument.getElementById('homeWelcomeHeading').innerText.includes('Aarav'), 'Welcome heading shows user name Aarav');

// -----------------------------------------------------------------
// Test 3: Log Out -> Verify Data DOES NOT SHOW on Screen
// -----------------------------------------------------------------
console.log('\n3. Testing Logout -> Screen Cleared, Data DOES NOT SHOW...');

handleLogout();

// Active state must be completely cleared
assert(STATE.user === null, 'STATE.user is null on logout');
assert(STATE.token === null, 'STATE.token is null on logout');
assertEqual(STATE.tasks.length, 0, 'STATE.tasks is cleared to 0 (data does NOT show)');
assertEqual(STATE.streak, 0, 'STATE.streak is reset to 0');
assert(localStorage.getItem('prepsync_token') === null, 'prepsync_token removed from storage');

// UI DOM must show 0 tasks and Guest state
assertEqual(mockDocument.getElementById('dockTaskBadge').innerText, 0, 'Dock task badge shows 0');
assertEqual(mockDocument.getElementById('homeStreakBadge').innerText, 0, 'Streak badge shows 0');
assert(mockDocument.getElementById('homeWelcomeHeading').innerText.includes('Welcome!'), 'Heading resets to Guest welcome');
assert(mockDocument.getElementById('taskQueueList').innerHTML.includes('empty'), 'Queue list shows empty state placeholder');
assert(mockDocument.getElementById('userHeaderSlot').innerHTML.includes('Log In'), 'Header slot shows Log In button');
assert(mockDocument.getElementById('profileMainContent').innerHTML.includes('Guest'), 'Profile tab displays Guest mode message');

// -----------------------------------------------------------------
// Test 4: Verify Data WAS STORED in Cache on Logout
// -----------------------------------------------------------------
console.log('\n4. Testing Data Storage -> Persisted in Storage on Logout...');

const storedCacheRaw = localStorage.getItem('prepsync_user_cache_demo@preppilot.com');
assert(storedCacheRaw !== null, 'User data is stored under prepsync_user_cache_demo@preppilot.com');

const storedCache = JSON.parse(storedCacheRaw);
assertEqual(storedCache.tasks.length, 2, 'Stored cache preserves 2 tasks');
assertEqual(storedCache.tasks[0].title, 'DSA Trees Practice', 'Stored task 1 matches');
assertEqual(storedCache.tasks[1].title, 'OS Deadlock Notes', 'Stored task 2 matches');
assertEqual(storedCache.streak, 15, 'Stored streak preserves 15 days');

// -----------------------------------------------------------------
// Test 5: Log In Again -> Verify Data COMES BACK
// -----------------------------------------------------------------
console.log('\n5. Testing Re-Login -> Saved Data Comes Back on Screen...');

handleDemoLogin();

assert(STATE.user !== null, 'User is logged back in');
assertEqual(STATE.user.email, 'demo@preppilot.com', 'Logged back in as demo@preppilot.com');
assertEqual(STATE.tasks.length, 2, 'All 2 previously saved tasks come back on screen');
assertEqual(STATE.tasks[0].title, 'DSA Trees Practice', 'Task 1 restored accurately');
assertEqual(STATE.tasks[1].title, 'OS Deadlock Notes', 'Task 2 restored accurately');
assertEqual(STATE.streak, 15, 'Streak 15 restored accurately');

// Check UI DOM elements after re-login
assertEqual(mockDocument.getElementById('dockTaskBadge').innerText, 2, 'Dock task badge restored to 2');
assertEqual(mockDocument.getElementById('homeStreakBadge').innerText, 15, 'Streak badge restored to 15');
assert(mockDocument.getElementById('homeWelcomeHeading').innerText.includes('Aarav'), 'Welcome heading restored for Aarav');

// -----------------------------------------------------------------
// Test 6: Custom User Signup / Login Workflow
// -----------------------------------------------------------------
console.log('\n6. Testing Custom User Account Login & Restoration...');

// Log out demo
handleLogout();
assertEqual(STATE.tasks.length, 0, 'Logged out clean');

// Custom user: John Doe
mockDocument.getElementById('authEmailInput').value = 'john.doe@college.edu';
mockDocument.getElementById('authPasswordInput').value = 'mypassword123';
mockDocument.getElementById('authNameInput').value = 'John Doe';

handleAuthSubmit({ preventDefault: () => {} });

assert(STATE.user !== null, 'John Doe is logged in');
assertEqual(STATE.user.email, 'john.doe@college.edu', 'Email is john.doe@college.edu');
assertEqual(STATE.tasks.length, 0, 'New user starts with 0 tasks');

// John adds a task
STATE.tasks.push({
  id: 'john-task-1',
  title: 'Database Normalization BCNF',
  subject: 'DBMS',
  type: 'hard',
  durationMin: 50,
  completed: false
});
persistState();
renderAllViews();
assertEqual(STATE.tasks.length, 1, 'John has 1 task');

// John logs out
handleLogout();
assertEqual(STATE.tasks.length, 0, 'John logged out: screen is clean');
assert(STATE.user === null, 'John logged out: user is null');

// Verify John's data was stored
const johnCacheRaw = localStorage.getItem('prepsync_user_cache_john.doe@college.edu');
assert(johnCacheRaw !== null, "John's data is stored in prepsync_user_cache_john.doe@college.edu");
const johnCache = JSON.parse(johnCacheRaw);
assertEqual(johnCache.tasks[0].title, 'Database Normalization BCNF', "John's task preserved");

// John logs back in
mockDocument.getElementById('authEmailInput').value = 'john.doe@college.edu';
mockDocument.getElementById('authPasswordInput').value = 'mypassword123';
handleAuthSubmit({ preventDefault: () => {} });

assertEqual(STATE.tasks.length, 1, "John's task comes back on re-login");
assertEqual(STATE.tasks[0].title, 'Database Normalization BCNF', "John's task restored correctly");

console.log('\n====================================================');
console.log(` RESULTS: ${passedTests} PASSED, ${failedTests} FAILED`);
console.log('====================================================\n');

if (failedTests > 0) {
  process.exit(1);
} else {
  console.log('🎉 ALL LOGOUT & RE-LOGIN PERSISTENCE TESTS PASSED!\n');
  process.exit(0);
}

/**
 * AdaptiveStudy AI - Core Application Engine & Helpers
 * Can be imported by test suites or loaded in script tag
 */

const DEFAULT_USER = {
  name: 'Aarav Sharma',
  email: 'aarav.sharma@college.edu',
  collegeId: '2024-CS-042',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
  track: 'btech_cse',
  goal: 'Score 9.0+ SGPA & Build 3 Coding Projects'
};

const DEFAULT_TASKS = [];

const STUDY_TRACKS = [
  { id: 'btech_cse', title: 'Computer Science (B.Tech)', sub: 'Coding, OS & Math' },
  { id: 'core_eng', title: 'Core Engineering', sub: 'Numericals & Lab Files' },
  { id: 'placements', title: 'Job Placements & Internships', sub: 'Aptitude & DSA Practice' },
  { id: 'exam_prep', title: 'Govt / Master Entrance (GATE)', sub: 'Theory & Previous Papers' }
];

function formatMinutesToTime(totalMinutes) {
  const normalized = ((totalMinutes % (24 * 60)) + (24 * 60)) % (24 * 60);
  const hours = Math.floor(normalized / 60);
  const minutes = normalized % 60;
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const displayH = hours % 12 === 0 ? 12 : hours % 12;
  return `${displayH}:${minutes < 10 ? `0${minutes}` : minutes} ${ampm}`;
}

function calculateSchedule(state) {
  const studyWindow = state.studyWindow || { start: '18:00', end: '23:00' };
  const lateOffset = state.lateOffset || 0;
  const tasks = state.tasks || [];

  const [startH, startM] = (studyWindow.start || '18:00').split(':').map(Number);
  const [endH, endM] = (studyWindow.end || '23:00').split(':').map(Number);
  let startMinTotal = startH * 60 + startM;
  let endMinTotal = endH * 60 + endM;

  if (endMinTotal <= startMinTotal) {
    endMinTotal += 24 * 60;
  }

  const totalMinsAllowed = endMinTotal - startMinTotal;
  let currentClock = startMinTotal + lateOffset;
  let accumulatedStudy = 0;

  const rank = { hard: 3, medium: 2, light: 1 };
  const sorted = [...tasks].sort((a, b) => {
    if (a.completed !== b.completed) return a.completed ? 1 : -1;
    return (rank[b.type] || 0) - (rank[a.type] || 0);
  });

  const timeline = [];
  let continuousWorkTime = 0;

  sorted.forEach((task, idx) => {
    if (continuousWorkTime >= 60) {
      const breakStart = currentClock;
      const breakEnd = breakStart + 15;
      timeline.push({
        id: `rest-${idx}`,
        isBreak: true,
        title: '☕ 15-Minute Refresh Break',
        subtitle: 'Step away from screen, drink water, stretch your legs.',
        start: formatMinutesToTime(breakStart),
        end: formatMinutesToTime(breakEnd),
        duration: 15
      });
      currentClock += 15;
      continuousWorkTime = 0;
    }

    const dur = task.durationMin;
    const isOverTime = (accumulatedStudy + dur) > totalMinsAllowed;
    const slotStart = currentClock;
    const slotEnd = slotStart + dur;

    timeline.push({
      id: `slot-${task.id}`,
      taskId: task.id,
      isBreak: false,
      title: task.title,
      subject: task.subject,
      type: task.type,
      start: formatMinutesToTime(slotStart),
      end: formatMinutesToTime(slotEnd),
      duration: dur,
      completed: task.completed,
      isOverTime: isOverTime,
      tag: isOverTime ? 'Shifted to Tomorrow' : task.type === 'hard' ? 'High Focus' : task.type === 'medium' ? 'Written Work' : 'Quick Review'
    });

    currentClock += dur;
    accumulatedStudy += dur;
    continuousWorkTime += dur;
  });

  return {
    timeline,
    totalStudy: accumulatedStudy,
    budget: totalMinsAllowed,
    isExceeded: accumulatedStudy > totalMinsAllowed,
    startFormatted: formatMinutesToTime(startMinTotal),
    endFormatted: formatMinutesToTime(endMinTotal)
  };
}

function parseNaturalLanguageTasks(rawText) {
  if (!rawText || !rawText.trim()) return [];
  const rawParts = rawText
    .split(/\n|,|;|\band\b/i)
    .map(p => p.trim())
    .filter(p => p.length > 3);

  const extracted = [];
  rawParts.forEach((phrase, idx) => {
    const lower = phrase.toLowerCase();
    let type = 'medium';
    let dur = 35;
    let subject = 'College Coursework';

    if (lower.includes('c ') || lower.includes('c++') || lower.includes('pointer') || lower.includes('code') || lower.includes('program') || lower.includes('dsa') || lower.includes('algo')) {
      subject = 'Data Structures';
    } else if (lower.includes('chemistry') || lower.includes('physics') || lower.includes('thermo') || lower.includes('lab') || lower.includes('record')) {
      subject = 'Applied Sciences';
    } else if (lower.includes('dbms') || lower.includes('sql') || lower.includes('database')) {
      subject = 'Database Systems';
    } else if (lower.includes('math') || lower.includes('calculus') || lower.includes('integral') || lower.includes('matrix')) {
      subject = 'Mathematics';
    } else if (lower.includes('os') || lower.includes('operating') || lower.includes('linux')) {
      subject = 'Operating Systems';
    }

    if (lower.includes('program') || lower.includes('code') || lower.includes('pointer') || lower.includes('solve') || lower.includes('calculus') || lower.includes('integral')) {
      type = 'hard';
      dur = 45;
    } else if (lower.includes('read') || lower.includes('slides') || lower.includes('revision') || lower.includes('skim') || lower.includes('review')) {
      type = 'light';
      dur = 20;
    } else if (lower.includes('lab') || lower.includes('record') || lower.includes('write') || lower.includes('submit') || lower.includes('file')) {
      type = 'medium';
      dur = 35;
    }

    const capitalized = phrase.charAt(0).toUpperCase() + phrase.slice(1);
    extracted.push({
      id: `task-${Date.now()}-${idx}`,
      title: capitalized,
      subject: subject,
      type: type,
      durationMin: dur,
      completed: false,
      progress: 0
    });
  });

  return extracted;
}

function generateMicroSteps(task) {
  const title = (task && task.title ? task.title : '').trim();
  const subject = (task && task.subject ? task.subject : '').trim();
  const type = task && task.type ? task.type : 'medium';
  const duration = task && task.durationMin ? task.durationMin : 35;
  const combined = (title + ' ' + subject).toLowerCase();

  // 1. Coding / Programming / DSA
  if (
    combined.includes('pointer') ||
    combined.includes('c++') ||
    combined.includes('c ') ||
    combined.includes('code') ||
    combined.includes('program') ||
    combined.includes('dsa') ||
    combined.includes('algo') ||
    combined.includes('python') ||
    combined.includes('java') ||
    combined.includes('tree') ||
    combined.includes('sql')
  ) {
    return {
      kickstart: `Open your code editor or notebook right now and write down the starter boilerplate. Don't worry about solving it yet.`,
      steps: [
        `Clarify the input format and test constraints on paper (5 mins)`,
        `Write the core logic loop and primary function for "${title || 'problem'}" without worrying about edge cases (15 mins)`,
        `Add boundary conditions, memory deallocation, and null checks (10 mins)`,
        `Compile and execute with 2 custom test inputs (5 mins)`
      ]
    };
  }

  // 2. Lab Record / Experiments / Chemistry / Physics
  if (
    combined.includes('record') ||
    combined.includes('lab') ||
    combined.includes('experiment') ||
    combined.includes('physics') ||
    combined.includes('chemistry') ||
    combined.includes('circuit') ||
    combined.includes('manual')
  ) {
    return {
      kickstart: `Lay out your record notebook, pens, and open the lab sheet PDF. Copy the experiment title first.`,
      steps: [
        `Write down the Aim, Apparatus required, and governing formula (8 mins)`,
        `Neatly sketch the circuit or experimental apparatus schematic (10 mins)`,
        `Enter sample observation readings and compute the percentage error (10 mins)`,
        `Write the 2-sentence conclusion, sign off, and pack your file (5 mins)`
      ]
    };
  }

  // 3. Slides / Reading / Revision
  if (
    combined.includes('slide') ||
    combined.includes('read') ||
    combined.includes('deck') ||
    combined.includes('chapter') ||
    combined.includes('skim') ||
    combined.includes('revision')
  ) {
    return {
      kickstart: `Open slide 1 right now and skim headings and bold text without taking notes.`,
      steps: [
        `Skim the first 5 slides and highlight 3 core concepts/definitions (6 mins)`,
        `Summarize key takeaways in 3 bullet points in your own words (8 mins)`,
        `Test yourself with 2 quick practice or interview questions (6 mins)`
      ]
    };
  }

  // 4. Mathematics / Calculus / Numericals
  if (
    combined.includes('math') ||
    combined.includes('calculus') ||
    combined.includes('integral') ||
    combined.includes('derivative') ||
    combined.includes('matrix') ||
    combined.includes('numerical') ||
    combined.includes('solve')
  ) {
    return {
      kickstart: `Open a fresh notebook page right now for "${title || 'math'}". Write down the governing formula to break the inertia.`,
      steps: [
        `Identify standard integral/derivative forms and substitution terms (7 mins)`,
        `Solve the primary problem step-by-step showing full working (15 mins)`,
        `Solve remaining problems and check substitutions and signs (10 mins)`,
        `Verify arithmetic and box the final answers neatly (5 mins)`
      ]
    };
  }

  // 5. Fallback based on difficulty type
  if (type === 'hard') {
    return {
      kickstart: `Open your code editor or notebook right now and write down the starter boilerplate. Don't worry about solving it yet.`,
      steps: [
        `Clarify the input format and test constraints on paper (5 mins)`,
        `Write the core logic loop without worrying about edge cases (15 mins)`,
        `Add boundary conditions and memory deallocation / null checks (10 mins)`,
        `Compile and execute with 2 custom test inputs (5 mins)`
      ]
    };
  } else if (type === 'medium') {
    return {
      kickstart: `Lay out your record notebook, pens, and open the lab sheet PDF. Copy the experiment title first.`,
      steps: [
        `Write down the Aim, Apparatus required, and governing formula (8 mins)`,
        `Neatly sketch the circuit or experimental apparatus schematic (10 mins)`,
        `Enter sample observation readings and compute the percentage error (10 mins)`,
        `Write the 2-sentence conclusion, sign off, and pack your file (5 mins)`
      ]
    };
  } else {
    return {
      kickstart: `Open slide 1 right now and skim headings and bold text without taking notes.`,
      steps: [
        `Skim the first 5 slides and highlight 3 core concepts/definitions (6 mins)`,
        `Summarize key takeaways in 3 bullet points in your own words (8 mins)`,
        `Test yourself with 2 quick practice or interview questions (6 mins)`
      ]
    };
  }
}

// Export for Node.js test environment if available
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DEFAULT_USER,
    DEFAULT_TASKS,
    STUDY_TRACKS,
    formatMinutesToTime,
    calculateSchedule,
    parseNaturalLanguageTasks,
    generateMicroSteps
  };
}

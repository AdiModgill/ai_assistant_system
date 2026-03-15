/* ─────────────────────────────────────────────────────────
   AI ASSISTANT – app.js
   Handles chat, sub-agent call simulation, and flow viz.
───────────────────────────────────────────────────────── */

/* ── CONFIG ─────────────────────────────────────────────── */
const SUB_AGENTS = [
  { id: 'weather',   name: 'Weather Agent',   icon: '🌤',  keywords: ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'wind'] },
  { id: 'email',     name: 'Email Agent',     icon: '✉️', keywords: ['email', 'mail', 'send', 'inbox', 'message'] },
  { id: 'whatsapp',  name: 'WhatsApp Agent',  icon: '💬',  keywords: ['whatsapp', 'chat', 'wa', 'reply', 'message'] },
  { id: 'clipboard', name: 'Clipboard Agent', icon: '📋',  keywords: ['clipboard', 'copy', 'paste', 'text'] },
];

const DEMO_RESPONSES = {
  weather: [
    'The current temperature in {city} is {temp}°C with {cond}.',
    'Weather data retrieved: {city} — {temp}°C, {cond}, wind {wind} km/h.',
  ],
  email: [
    'Email drafted and queued for sending to {to}.',
    'I found {n} unread emails in your inbox. Want me to summarise them?',
  ],
  whatsapp: [
    'WhatsApp reply sent to {contact}.',
    'Scheduled WhatsApp message to {contact} at {time}.',
  ],
  clipboard: [
    'Clipboard content analysed — detected {type}.',
    'Text copied to clipboard successfully.',
  ],
  default: [
    "I've processed your request.",
    "Done! Let me know if you need anything else.",
    "Sure, I've taken care of that for you.",
  ],
};

/* ── STATE ───────────────────────────────────────────────── */
let isBusy = false;

/* ── DOM REFS ────────────────────────────────────────────── */
const inputEl   = document.getElementById('userInput');
const messagesEl = document.getElementById('messages');
const agentListEl = document.getElementById('agentList');
const flowArrowsEl = document.getElementById('flowArrows');
const subNodesEl   = document.getElementById('subNodes');
const mainNodeEl   = document.getElementById('mainNode');

/* ── INIT ────────────────────────────────────────────────── */
buildFlowVisualizer();
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });

/* ── FLOW VISUALIZER ─────────────────────────────────────── */
function buildFlowVisualizer() {
  // connector line + sub-nodes
  const line = document.createElement('div');
  line.className = 'flow-line';
  line.innerHTML = '<div class="flow-dash" id="fd-main"></div>'
                 + '<div class="flow-arrowhead" id="fa-main"></div>';
  flowArrowsEl.appendChild(line);

  SUB_AGENTS.forEach((ag) => {
    const node = document.createElement('div');
    node.className = 'sub-flow-node';
    node.id = `fn-${ag.id}`;
    node.innerHTML = `
      <div class="flow-icon">${ag.icon}</div>
      <span class="flow-label">${ag.name.replace(' Agent', '')}</span>`;
    subNodesEl.appendChild(node);
  });
}

function activateFlowNode(agentId) {
  // light up main node arrow
  document.getElementById('fd-main')?.classList.add('lit');
  document.getElementById('fa-main')?.classList.add('lit');
  mainNodeEl.classList.add('active-node');

  // activate sub-node
  const node = document.getElementById(`fn-${agentId}`);
  if (node) node.classList.add('active-sub');
}

function resetFlowVisualizer() {
  document.getElementById('fd-main')?.classList.remove('lit');
  document.getElementById('fa-main')?.classList.remove('lit');
  mainNodeEl.classList.remove('active-node');
  SUB_AGENTS.forEach((ag) => {
    document.getElementById(`fn-${ag.id}`)?.classList.remove('active-sub');
  });
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
function setSidebarStatus(agentId, status) {
  const items = agentListEl.querySelectorAll('.agent-item');
  items.forEach((item) => {
    if (item.dataset.agent === agentId) {
      const badge = item.querySelector('.agent-status');
      badge.className = `agent-status ${status}`;
      badge.textContent = status === 'idle' ? 'Idle'
                        : status === 'calling' ? 'Calling…'
                        : status === 'done' ? 'Done'
                        : status;
      if (status === 'calling') {
        item.classList.add('calling');
      } else {
        item.classList.remove('calling');
      }
    }
  });
}

/* ── CHAT HELPERS ────────────────────────────────────────── */
function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendUserMessage(text) {
  const el = document.createElement('div');
  el.className = 'message user';
  el.innerHTML = `
    <span class="msg-avatar">🧑</span>
    <div class="msg-bubble">
      ${escHtml(text)}
      <span class="msg-meta">You • ${now()}</span>
    </div>`;
  messagesEl.appendChild(el);
  scrollBottom();
}

function appendAssistantMessage(text, agentName = 'Main Agent', agentIcon = '🤖') {
  const el = document.createElement('div');
  el.className = 'message assistant';
  el.innerHTML = `
    <span class="msg-avatar">${agentIcon}</span>
    <div class="msg-bubble">
      ${escHtml(text)}
      <span class="msg-meta">${agentName} • ${now()}</span>
    </div>`;
  messagesEl.appendChild(el);
  scrollBottom();
}

function appendSubAgentCard(state, agentIcon, agentName, text) {
  const el = document.createElement('div');
  el.className = `subagent-card ${state}`;
  el.innerHTML = `
    <span class="subagent-card-icon">${agentIcon}</span>
    <div class="subagent-card-body">
      <span class="subagent-card-title">${state === 'calling' ? '⟳ Calling' : '✓ Response from'} ${agentName}</span>
      <span class="subagent-card-text">${escHtml(text)}</span>
    </div>`;
  messagesEl.appendChild(el);
  scrollBottom();
  return el;
}

function showTyping(avatar = '🤖') {
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typingIndicator';
  el.innerHTML = `
    <span class="msg-avatar">${avatar}</span>
    <div class="typing-dots"><span></span><span></span><span></span></div>`;
  messagesEl.appendChild(el);
  scrollBottom();
}

function removeTyping() {
  document.getElementById('typingIndicator')?.remove();
}

function scrollBottom() {
  const section = document.querySelector('.chat-section');
  section.scrollTop = section.scrollHeight;
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ── AGENT DETECTION ─────────────────────────────────────── */
function detectAgent(text) {
  const lower = text.toLowerCase();
  for (const ag of SUB_AGENTS) {
    if (ag.keywords.some((k) => lower.includes(k))) return ag;
  }
  return null;
}

/* ── DEMO RESPONSE GENERATOR ─────────────────────────────── */
function demoResponse(agentId, userText) {
  const pool = DEMO_RESPONSES[agentId] || DEMO_RESPONSES.default;
  let tpl = pool[Math.floor(Math.random() * pool.length)];

  // fill in placeholders
  const cities = ['London','Tokyo','Mumbai','New York','Sydney'];
  const contacts = ['Rahul','Mom','Priya','Arjun'];
  const types = ['code snippet','URL','plain text','phone number'];

  tpl = tpl
    .replace('{city}', cities[Math.floor(Math.random()*cities.length)])
    .replace('{temp}', Math.floor(Math.random()*25)+10)
    .replace('{cond}', ['clear skies','light clouds','light rain','heavy fog'][Math.floor(Math.random()*4)])
    .replace('{wind}', Math.floor(Math.random()*20)+5)
    .replace('{to}', 'recipient@example.com')
    .replace('{n}', Math.floor(Math.random()*10)+1)
    .replace('{contact}', contacts[Math.floor(Math.random()*contacts.length)])
    .replace('{time}', '3:00 PM')
    .replace('{type}', types[Math.floor(Math.random()*types.length)]);

  return tpl;
}

function mainSummary(agentName, subResponse) {
  return `Sub-agent (${agentName}) responded: "${subResponse}" — task complete.`;
}

/* ── MAIN SEND FLOW ──────────────────────────────────────── */
async function sendMessage() {
  if (isBusy) return;
  const text = inputEl.value.trim();
  if (!text) return;

  isBusy = true;
  inputEl.value = '';
  inputEl.disabled = true;

  // 1. Show user message
  appendUserMessage(text);

  // 2. Detect sub-agent
  const agent = detectAgent(text);

  if (agent) {
    // ── PATH A: sub-agent is needed ───────────────────────

    // Show "main agent thinking"
    showTyping('🤖');
    await delay(900);
    removeTyping();

    // Main agent announces delegation
    appendAssistantMessage(`I'll delegate this to the ${agent.name}.`, 'Main Agent');

    await delay(400);

    // Show calling card
    appendSubAgentCard('calling', agent.icon, agent.name, `Processing: "${text}"`);

    // Activate sidebar + flow
    setSidebarStatus(agent.id, 'calling');
    activateFlowNode(agent.id);

    // Sub-agent "thinking"
    showTyping(agent.icon);
    await delay(1400);
    removeTyping();

    // Sub-agent response
    const subReply = demoResponse(agent.id, text);
    const subCard = appendSubAgentCard('done', agent.icon, agent.name, subReply);
    setSidebarStatus(agent.id, 'done');

    await delay(600);

    // Main agent receives + summarises
    showTyping('🤖');
    await delay(800);
    removeTyping();

    appendAssistantMessage(mainSummary(agent.name, subReply), 'Main Agent');

    // Reset sidebar + flow after 2.5 s
    await delay(2500);
    setSidebarStatus(agent.id, 'idle');
    resetFlowVisualizer();

  } else {
    // ── PATH B: main agent handles directly ───────────────

    showTyping('🤖');
    await delay(1100);
    removeTyping();

    const replies = DEMO_RESPONSES.default;
    appendAssistantMessage(replies[Math.floor(Math.random()*replies.length)], 'Main Agent');
  }

  isBusy = false;
  inputEl.disabled = false;
  inputEl.focus();
}

/* ── HINT TOAST ──────────────────────────────────────────── */
function showHint() {
  let toast = document.querySelector('.hint-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'hint-toast';
    toast.textContent = 'Try: "What\'s the weather in Tokyo?" or "Send an email to John"';
    document.body.appendChild(toast);
  }
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

/* ── UTILS ───────────────────────────────────────────────── */
function delay(ms) { return new Promise((r) => setTimeout(r, ms)); }

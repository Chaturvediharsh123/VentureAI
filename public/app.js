// ─── State ────────────────────────────────────────────────────────────────
const agentBuffers = { research: '', strategy: '', finance: '', tech: '', marketing: '', presentation: '' };
let currentSlide = 0;
let slides = [];
let isBuilding = false;

// ─── Load API key from server env on startup ───────────────────────────────
async function loadConfig() {
  try {
    const res = await fetch('/api/config');
    const data = await res.json();
    if (data.apiKey) {
      document.getElementById('apiKey').value = data.apiKey;
    }
  } catch (e) {
    // silently ignore — user can type their key manually
  }
}

// ─── Marked.js config ──────────────────────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true });

// ─── Tab switching ─────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('pane-' + name).classList.add('active');
}

// ─── Agent card state ──────────────────────────────────────────────────────
const AGENT_LABELS = {
  research: '🔍 Research Agent',
  strategy: '💼 Strategy Agent',
  finance: '📊 Finance Agent',
  tech: '💻 Tech Agent',
  marketing: '📢 Marketing Agent',
  presentation: '📄 Presentation Agent',
};

function setAgentRunning(agent) {
  const card = document.getElementById('card-' + agent);
  const badge = document.getElementById('badge-' + agent);
  card.classList.add('running');
  card.classList.remove('done');
  badge.textContent = '⚡ Thinking...';
  document.getElementById('currentAgentLabel').textContent = AGENT_LABELS[agent] + ' is working...';
  document.getElementById('pipelineStatus').textContent = AGENT_LABELS[agent] + ' is analyzing your idea...';

  // Show results section and activate the tab for the current agent
  document.getElementById('results-section').style.display = 'block';
  switchTab(agent);
}

function setAgentDone(agent) {
  const card = document.getElementById('card-' + agent);
  const badge = document.getElementById('badge-' + agent);
  card.classList.remove('running');
  card.classList.add('done');
  badge.textContent = '✅ Done';
}

// ─── Render markdown into a content div ───────────────────────────────────
function renderMarkdown(agent) {
  const el = document.getElementById('content-' + agent);
  if (!el) return;
  el.classList.remove('streaming-cursor');
  el.innerHTML = marked.parse(agentBuffers[agent] || '');
}

// ─── Pitch Deck Renderer ──────────────────────────────────────────────────
function renderPitchDeck(jsonText) {
  let data;
  try {
    // Strip possible markdown code fences
    const cleaned = jsonText.replace(/```json?/gi, '').replace(/```/g, '').trim();
    data = JSON.parse(cleaned);
  } catch (e) {
    // Try to extract JSON array from the text
    const match = jsonText.match(/\[[\s\S]*\]/);
    if (match) {
      try { data = JSON.parse(match[0]); } catch { data = null; }
    }
  }

  const loading = document.getElementById('deck-loading');
  const container = document.getElementById('deck-container');

  if (!data || !Array.isArray(data) || data.length === 0) {
    loading.innerHTML = `<p style="color:var(--text-secondary);padding:20px;">Could not parse pitch deck. Raw output displayed below.</p>
      <pre style="color:var(--text-muted);font-size:12px;overflow:auto;max-height:400px;">${jsonText}</pre>`;
    return;
  }

  slides = data;
  loading.style.display = 'none';
  container.style.display = 'block';

  const slidesEl = document.getElementById('deck-slides');
  const progressEl = document.getElementById('deckProgress');
  slidesEl.innerHTML = '';
  progressEl.innerHTML = '';

  slides.forEach((slide, i) => {
    // Slide HTML
    const div = document.createElement('div');
    div.className = 'deck-slide' + (i === 0 ? ' active' : '');
    div.id = 'slide-' + i;
    div.innerHTML = `
      <div class="slide-card">
        <div>
          <div class="slide-number">Slide ${slide.slideNumber} of ${slides.length}</div>
          <span class="slide-emoji">${slide.emoji || '🚀'}</span>
          <div class="slide-title">${escapeHtml(slide.title || '')}</div>
          <div class="slide-subtitle">${escapeHtml(slide.subtitle || '')}</div>
          <ul class="slide-bullets">
            ${(slide.bullets || []).map(b => `<li>${escapeHtml(b)}</li>`).join('')}
          </ul>
          ${slide.highlight ? `<div class="slide-highlight">${escapeHtml(slide.highlight)}</div>` : ''}
        </div>
        ${slide.speakerNote ? `
        <div class="slide-speaker-note">
          <div class="slide-note-label">🎤 Speaker Note</div>
          ${escapeHtml(slide.speakerNote)}
        </div>` : ''}
      </div>`;
    slidesEl.appendChild(div);

    // Progress dot
    const dot = document.createElement('div');
    dot.className = 'deck-dot' + (i === 0 ? ' active' : '');
    dot.id = 'dot-' + i;
    dot.onclick = () => goToSlide(i);
    progressEl.appendChild(dot);
  });

  currentSlide = 0;
  updateDeckNav();
}

function goToSlide(index) {
  document.querySelectorAll('.deck-slide').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.deck-dot').forEach(d => d.classList.remove('active'));
  currentSlide = index;
  document.getElementById('slide-' + index).classList.add('active');
  document.getElementById('dot-' + index).classList.add('active');
  updateDeckNav();
}

function changeSlide(dir) {
  const next = currentSlide + dir;
  if (next < 0 || next >= slides.length) return;
  goToSlide(next);
}

function updateDeckNav() {
  document.getElementById('prevSlide').disabled = currentSlide === 0;
  document.getElementById('nextSlide').disabled = currentSlide === slides.length - 1;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── Toast ─────────────────────────────────────────────────────────────────
function showToast(msg) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 6000);
}

// ─── Main Build Function ───────────────────────────────────────────────────
async function startBuild() {
  if (isBuilding) return;

  const idea = document.getElementById('businessIdea').value.trim();
  const apiKey = document.getElementById('apiKey').value.trim();

  if (!idea) { showToast('⚠️ Please enter your business idea first.'); return; }
  if (!apiKey) { showToast('⚠️ Please enter your Gemini API key.'); return; }

  isBuilding = true;
  const btn = document.getElementById('buildBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Building...';

  // Reset state
  Object.keys(agentBuffers).forEach(k => { agentBuffers[k] = ''; });
  ['research','strategy','finance','tech','marketing','presentation'].forEach(agent => {
    const card = document.getElementById('card-' + agent);
    const badge = document.getElementById('badge-' + agent);
    card.classList.remove('running','done');
    badge.textContent = 'Waiting';
    const el = document.getElementById('content-' + agent);
    if (el) el.innerHTML = '<div class="placeholder-lines"><div class="shimmer-placeholder"></div><div class="shimmer-placeholder"></div><div class="shimmer-placeholder"></div></div>';
  });
  document.getElementById('deck-loading').style.display = 'block';
  document.getElementById('deck-container').style.display = 'none';
  document.getElementById('deck-loading').innerHTML = '<div class="placeholder-lines"><div class="shimmer-placeholder"></div><div class="shimmer-placeholder"></div></div>';

  // Show pipeline
  document.getElementById('pipeline-section').style.display = 'block';
  document.getElementById('pipeline-section').scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea, apiKey }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Server error');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line

      let currentEvent = null;
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim();
          try {
            const data = JSON.parse(raw);
            handleEvent(currentEvent, data);
          } catch {}
        }
      }
    }
  } catch (err) {
    showToast('❌ ' + (err.message || 'Something went wrong. Check your API key and try again.'));
    document.getElementById('pipelineStatus').textContent = 'Pipeline failed. Please try again.';
  } finally {
    isBuilding = false;
    btn.disabled = false;
    btn.textContent = '🚀 Build My Startup';
  }
}

// ─── SSE Event handler ─────────────────────────────────────────────────────
// ─── Init ─────────────────────────────────────────────────────────────────
loadConfig();

function handleEvent(event, data) {
  switch (event) {
    case 'agentStart':
      setAgentRunning(data.agent);
      // Add streaming cursor to content area
      const el = document.getElementById('content-' + data.agent);
      if (el) { el.innerHTML = ''; el.classList.add('streaming-cursor'); }
      break;

    case 'chunk':
      agentBuffers[data.agent] += data.text;
      // Live-render the current agent's content
      const contentEl = document.getElementById('content-' + data.agent);
      if (contentEl) {
        contentEl.innerHTML = marked.parse(agentBuffers[data.agent]);
        contentEl.classList.add('streaming-cursor');
      }
      break;

    case 'agentDone':
      setAgentDone(data.agent);
      renderMarkdown(data.agent);
      break;

    case 'complete':
      // Final render of all agents
      ['research','strategy','finance','tech','marketing'].forEach(a => {
        if (data[a]) { agentBuffers[a] = data[a]; renderMarkdown(a); }
      });
      renderPitchDeck(data.presentation || agentBuffers.presentation);

      document.getElementById('pipelineStatus').textContent = '🎉 All 6 agents completed successfully!';
      document.getElementById('currentAgentLabel').textContent = '✅ Pipeline complete';
      document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
      break;

    case 'error':
      showToast('❌ ' + (data.message || 'Agent error occurred.'));
      document.getElementById('pipelineStatus').textContent = 'Error: ' + (data.message || 'Unknown error');
      break;
  }
}

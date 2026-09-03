let eventCounter = 1;

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('initTime').textContent = new Date().toLocaleTimeString();
  fetchTelemetry();
  setInterval(fetchTelemetry, 3000);
});

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

async function fetchTelemetry() {
  try {
    const res = await fetch('/api/telemetry');
    if (!res.ok) throw new Error('Telemetry request failed');
    const data = await res.json();
    updateUI(data);
  } catch (err) {
    console.error('Telemetry error:', err);
  }
}

function updateUI(data) {
  const bat = data.battery;
  const pct = bat.percentage || 0;

  // Battery Pct & Status
  document.getElementById('batteryPct').textContent = `${pct}%`;
  document.getElementById('batteryStatus').textContent = bat.status || 'UNKNOWN';
  document.getElementById('batteryPlugged').textContent = bat.plugged || 'UNPLUGGED';
  document.getElementById('batteryTemp').textContent = `${bat.temperature}°C`;
  document.getElementById('batteryHealth').textContent = bat.health || 'GOOD';

  // Update SVG Circle Offset (Circumference ~314)
  const circle = document.getElementById('batteryGauge');
  const circumference = 314;
  const offset = circumference - (pct / 100) * circumference;
  circle.style.strokeDashoffset = offset;

  // Gauge color based on level
  if (pct <= 20) {
    circle.style.stroke = 'var(--accent-coral)';
    addEvent(`⚠️ Battery Low (${pct}%)! Connect charger.`, 'warning');
  } else if (pct <= 40) {
    circle.style.stroke = 'var(--accent-yellow)';
  } else {
    circle.style.stroke = 'var(--accent-cyan)';
  }

  // OpenClaw Gateway
  const gw = data.openclaw;
  const gwBadge = document.getElementById('gwBadge');
  document.getElementById('gwUrl').textContent = gw.gatewayUrl || 'http://127.0.0.1:18789/';
  document.getElementById('gwModel').textContent = `Model: ${gw.model || 'google/gemini-3.5-flash'}`;

  if (gw.status === 'online') {
    gwBadge.textContent = 'ONLINE';
    gwBadge.className = 'badge online';
  } else {
    gwBadge.textContent = 'OFFLINE';
    gwBadge.className = 'badge warning';
  }

  // Device Info
  if (data.device) {
    document.getElementById('deviceModel').textContent = data.device.model;
    document.getElementById('deviceOs').textContent = data.device.os;
    document.getElementById('deviceArch').textContent = data.device.arch;
  }
}

async function fetchClipboard() {
  try {
    showToast('Fetching Android Clipboard...');
    const res = await fetch('/api/clip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: '' })
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(`Error: ${err.error || 'Failed'}`);
      return;
    }

    const data = await res.json();
    document.getElementById('clipText').value = data.input || '';
    displayResult(data.result);
    showToast('Clipboard fetched and processed with Claw 🦀!');
    addEvent('📋 ClawClip processed Android clipboard content.');
  } catch (err) {
    showToast('Error fetching clipboard');
  }
}

async function processAIClip() {
  const text = document.getElementById('clipText').value;
  if (!text || !text.trim()) {
    showToast('Please enter or paste text first!');
    return;
  }

  const btn = document.getElementById('processBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Processing with Claw 🦀...';

  try {
    const res = await fetch('/api/clip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    const data = await res.json();
    if (res.ok) {
      displayResult(data.result);
      showToast('Result copied to Android clipboard!');
      addEvent('✨ ClawClip completed AI summary.');
    } else {
      showToast(`Error: ${data.error}`);
    }
  } catch (err) {
    showToast('Processing error');
  } finally {
    btn.disabled = false;
    btn.textContent = '✨ Process with Claw 🦀';
  }
}

function displayResult(resultText) {
  const wrapper = document.getElementById('clipOutputWrapper');
  const content = document.getElementById('clipResult');
  content.textContent = resultText;
  wrapper.classList.remove('hidden');
}

function copyResult() {
  const content = document.getElementById('clipResult').textContent;
  navigator.clipboard.writeText(content);
  showToast('Result copied to clipboard!');
}

function addEvent(msg, type = 'info') {
  const stream = document.getElementById('eventStream');
  const countBadge = document.getElementById('eventCount');

  // Prevent duplicate consecutive messages
  const firstMsg = stream.querySelector('.event-msg');
  if (firstMsg && firstMsg.textContent === msg) return;

  const item = document.createElement('div');
  item.className = `event-item ${type}`;

  const timeSpan = document.createElement('span');
  timeSpan.className = 'event-time';
  timeSpan.textContent = new Date().toLocaleTimeString();

  const msgSpan = document.createElement('span');
  msgSpan.className = 'event-msg';
  msgSpan.textContent = msg;

  item.appendChild(timeSpan);
  item.appendChild(msgSpan);

  stream.insertBefore(item, stream.firstChild);

  eventCounter++;
  countBadge.textContent = `${eventCounter} Events`;
}

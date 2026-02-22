/**
 * chat.js – AI Chat Panel (Ollama SSE Streaming)
 * Auto-detects LLM availability. Streams response token-by-token.
 */

let llmAvailable = false;
let currentContext = null;
const API_BASE = '';  // same-origin

export async function initChat() {
    await checkLLMStatus();

    document.getElementById('chat-toggle').addEventListener('click', toggleChat);
    document.getElementById('chat-close').addEventListener('click', closeChat);
    document.getElementById('chat-send').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

export function setContext(level, data) {
    const summaries = {
        l1: `Level 1 (Dijkstra): ${data.stats?.total_nodes} nodes, ${data.stats?.total_edges} edges. Max distance: ${data.stats?.max_distance}.`,
        l2: `Level 2 (Truck Assignment): ${data.assignments?.length} trucks, avg utilization ${data.stats?.utilisation_moyenne_pct}%.`,
        l3: `Level 3 (Weekly Schedule): ${data.stats?.jours_planifies} days planned.`,
        l4: `Level 4 (VRP): Initial dist ${data.performance?.distance_initiale}, optimized ${data.performance?.distance_optimisee}, gain ${data.performance?.amelioration_pct}%.`,
        l5: `Level 5 (Real-time): ${data.kpis?.nb_alertes} alerts, ${data.kpis?.efficacite_collecte}% efficiency at tick ${data.tick}.`,
    };
    currentContext = summaries[level] || null;
    const ctxDisplay = document.getElementById('chat-ctx-display');
    if (ctxDisplay) ctxDisplay.textContent = currentContext || 'none';
}

async function checkLLMStatus() {
    const badge = document.getElementById('chat-model-badge');
    const dot = document.getElementById('chat-status-dot');
    try {
        const res = await fetch(`${API_BASE}/api/chat/status`, { method: 'POST' });
        const data = await res.json();
        llmAvailable = data.available;
        if (llmAvailable) {
            badge.textContent = data.models?.[0] || 'llama3.2:3b';
            dot.classList.add('ready');
            appendMessage('assistant',
                `✅ **Ollama detected!** Model: \`${data.models?.[0] || 'unknown'}\`\n\nI'm CyberCollect AI. Ask me anything about the route optimization algorithms, or run a level and I'll explain the results!`
            );
        } else {
            badge.textContent = 'offline';
            appendMessage('assistant',
                '⚠️ **No LLM detected.**\n\n' + (data.message || '') +
                '\n\nOnce Ollama is running on this machine (or server), the chat will activate automatically.'
            );
        }
    } catch {
        badge.textContent = 'error';
        appendMessage('assistant', '⚠️ Could not reach backend. Make sure the server is running.');
    }
}

function toggleChat() {
    const drawer = document.getElementById('chat-drawer');
    drawer.classList.toggle('open');
}

function closeChat() {
    document.getElementById('chat-drawer').classList.remove('open');
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    appendMessage('user', msg);

    const assistantDiv = appendMessage('assistant', '');
    assistantDiv.classList.add('typing-cursor');

    try {
        const res = await fetch(`${API_BASE}/api/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, context: currentContext }),
        });

        if (!res.ok) throw new Error('Stream error');

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const raw = decoder.decode(value);
            const lines = raw.split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const chunk = JSON.parse(line.slice(6));
                        if (chunk.token) {
                            fullText += chunk.token;
                            assistantDiv.classList.remove('typing-cursor');
                            assistantDiv.innerHTML = _md(fullText);
                            assistantDiv.classList.add('typing-cursor');
                            _scrollToBottom();
                        }
                        if (chunk.done) {
                            assistantDiv.classList.remove('typing-cursor');
                        }
                    } catch { }
                }
            }
        }
        assistantDiv.classList.remove('typing-cursor');
    } catch (err) {
        assistantDiv.classList.remove('typing-cursor');
        assistantDiv.textContent = '⚠️ Error: ' + err.message;
    }
}

function appendMessage(role, content) {
    const messages = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    const avatar = role === 'assistant' ? 'AI' : 'YOU';
    div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-content">${_md(content)}</div>
  `;
    messages.appendChild(div);
    _scrollToBottom();
    return div.querySelector('.msg-content');
}

function _scrollToBottom() {
    const messages = document.getElementById('chat-messages');
    messages.scrollTop = messages.scrollHeight;
}

// Minimal inline markdown renderer (bold, code, newlines)
function _md(text) {
    return text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(0,212,255,0.1);padding:1px 4px;border-radius:2px;color:var(--neon-blue)">$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong style="color:var(--neon-green)">$1</strong>')
        .replace(/\n/g, '<br>');
}

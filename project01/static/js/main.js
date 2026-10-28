// ─── Modal Toggle ────────────────────────────────────────────────────────────
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    } else {
        modal.style.display = 'flex';
        void modal.offsetWidth;
        modal.classList.add('show');
    }
}
window.onclick = function(e) {
    if (e.target.classList.contains('modal')) toggleModal(e.target.id);
};

// ─── Table Search ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss flash alerts
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(el => {
            el.style.opacity = '0';
            el.style.transition = 'opacity .5s';
            setTimeout(() => el.remove(), 500);
        });
    }, 5000);

    // Table search
    const s = document.getElementById('tableSearch');
    if (s) {
        s.addEventListener('keyup', () => {
            const f = s.value.toLowerCase();
            const tbl = document.getElementById('cropsTable');
            if (!tbl) return;
            Array.from(tbl.getElementsByTagName('tr')).slice(1).forEach(tr => {
                if (tr.querySelector('.empty-state')) return;
                tr.style.display = tr.textContent.toLowerCase().includes(f) ? '' : 'none';
            });
        });
    }

    // Pre-select crop from URL params
    const params = new URLSearchParams(window.location.search);
    const crop = params.get('crop');
    if (crop) {
        ['p_crop','d_crop','r_crop','irr_crop'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = crop;
        });
    }
});

// ─── AI AgriBot Chat ─────────────────────────────────────────────────────────
function toggleAIChat() {
    document.getElementById('aiChatWindow').classList.toggle('open');
}

function handleAIKeyPress(e) {
    if (e.key === 'Enter') sendAIMessage();
}

async function sendAIMessage() {
    const input = document.getElementById('aiInput');
    const msg = input.value.trim();
    if (!msg) return;

    const container = document.getElementById('aiMessages');
    appendMsg(container, msg, 'msg-user');
    input.value = '';
    container.scrollTop = container.scrollHeight;

    // Loading dot
    const loading = document.createElement('div');
    loading.className = 'ai-msg msg-system';
    loading.innerHTML = '<span class="loading-dots">•••</span>';
    container.appendChild(loading);
    container.scrollTop = container.scrollHeight;

    try {
        const res = await fetch('/api/agribot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        loading.remove();
        const div = document.createElement('div');
        div.className = 'ai-msg msg-system';
        div.innerHTML = data.response || 'I am here to help with your farming queries!';
        container.appendChild(div);
    } catch {
        loading.innerHTML = 'Sorry, I could not connect. Please try again.';
    }
    container.scrollTop = container.scrollHeight;
}

function appendMsg(container, text, cls) {
    const div = document.createElement('div');
    div.className = 'ai-msg ' + cls;
    div.textContent = text;
    container.appendChild(div);
}

// ─── Tamil Voice Assistant ───────────────────────────────────────────────────
async function sendTamilMessage() {
    const input = document.getElementById('tamilInput');
    const query = input.value.trim();
    if (!query) return;

    try {
        const res = await fetch('/api/tamil-assistant', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query})
        });
        const data = await res.json();
        const resp = document.getElementById('tamilResponse');
        resp.textContent = data.response;
        resp.style.display = 'block';
        input.value = '';

        // Text-to-speech for Tamil response
        if ('speechSynthesis' in window) {
            const utt = new SpeechSynthesisUtterance(data.response);
            utt.lang = 'ta-IN';
            utt.rate = 0.9;
            window.speechSynthesis.speak(utt);
        }
    } catch (e) {
        console.error(e);
    }
}

let recognition = null;
function startVoice() {
    const btn = document.getElementById('voiceBtn');
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert('Voice input is not supported in this browser. Please use Chrome.');
        return;
    }
    if (recognition && recognition.active) {
        recognition.stop();
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'ta-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.active = true;
    btn.classList.add('recording');

    recognition.onresult = function(e) {
        const transcript = e.results[0][0].transcript;
        document.getElementById('tamilInput').value = transcript;
        btn.classList.remove('recording');
        recognition.active = false;
        sendTamilMessage();
    };
    recognition.onerror = recognition.onend = function() {
        btn.classList.remove('recording');
        recognition.active = false;
    };
    recognition.start();
}

// ─── Score Bar Animation ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.querySelectorAll('.score-fill').forEach(bar => {
                    const w = bar.style.width;
                    bar.style.width = '0';
                    setTimeout(() => bar.style.width = w, 100);
                });
            }
        });
    });
    document.querySelectorAll('.rec-card').forEach(el => observer.observe(el));
});

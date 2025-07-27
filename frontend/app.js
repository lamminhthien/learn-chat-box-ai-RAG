// API
let API_ENDPOINT = `http://localhost:8000`

// ========== CHAT HISTORY ========== //
let chatHistory = [];

// ========== CHAT ========== //
function renderChat() {
    const chatbox = document.getElementById('chatbox');
    if (!chatbox) return;
    chatbox.innerHTML = '';
    chatHistory.forEach((msg, idx) => {
        const div = document.createElement('div');
        div.className = `chat-bubble ${msg.sender}`;
        if (msg.sender === 'user') {
            div.innerHTML = `<span class="avatar">👤</span><span>${msg.text}</span>`;
        } else {
            div.innerHTML = `<span class="avatar">🤖</span><span>${msg.text}</span>` +
                `<button class="tts-btn" title="Đọc" onclick="speakText(\`${msg.text.replace(/`/g, '\`')}\`)">🔊</button>`;
        }
        chatbox.appendChild(div);
    });
    chatbox.scrollTop = chatbox.scrollHeight;
}

const chatForm = document.getElementById('chat-form');
if (chatForm) {
    chatForm.onsubmit = function(e) {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        const text = input.value.trim();
        if (!text) return;
        chatHistory.push({ sender: 'user', text });
        renderChat();
        input.value = '';
        // Gửi request tới backend
        fetch(`${API_ENDPOINT}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        })
        .then(res => res.json())
        .then(data => {
            chatHistory.push({ sender: 'bot', text: data.reply });
            renderChat();
        })
        .catch(() => {
            chatHistory.push({ sender: 'bot', text: 'Không thể kết nối backend.' });
            renderChat();
        });
    };
}

// ========== TEXT-TO-SPEECH (TTS) ========== //
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = 'vi-VN';
        window.speechSynthesis.speak(utter);
    }
}
window.speakText = speakText;

// ========== SIDEBAR MENU LOGIC ========== //
const sidebarHome = document.getElementById('sidebar-home');
const sidebarSchedule = document.getElementById('sidebar-schedule');
const chatFormEl = document.getElementById('chat-form');
const chatboxEl = document.getElementById('chatbox');
const scheduleFormEl = document.getElementById('schedule-form');

if (sidebarHome && sidebarSchedule && chatFormEl && chatboxEl && scheduleFormEl) {
    sidebarHome.onclick = function() {
        sidebarHome.classList.add('active');
        sidebarSchedule.classList.remove('active');
        chatFormEl.style.display = '';
        chatboxEl.style.display = '';
        scheduleFormEl.style.display = 'none';
    };
    sidebarSchedule.onclick = function() {
        sidebarHome.classList.remove('active');
        sidebarSchedule.classList.add('active');
        chatFormEl.style.display = 'none';
        chatboxEl.style.display = 'none';
        scheduleFormEl.style.display = '';
    };
}

// ========== ĐẶT LỊCH HẸN ========== //
if (scheduleFormEl) {
    scheduleFormEl.onsubmit = function(e) {
        e.preventDefault();
        const title = document.getElementById('event-title').value.trim();
        const datetime = document.getElementById('event-datetime').value;
        if (!title || !datetime) return;
        // Gửi request lên backend nếu muốn, hoặc chỉ hiển thị thông báo
        alert('Đã tạo lịch hẹn: ' + title + ' lúc ' + datetime);
        scheduleFormEl.reset();
        // Chuyển về chat sau khi tạo lịch
        if (sidebarHome && sidebarSchedule && chatFormEl && chatboxEl && scheduleFormEl) {
            sidebarHome.classList.add('active');
            sidebarSchedule.classList.remove('active');
            chatFormEl.style.display = '';
            chatboxEl.style.display = '';
            scheduleFormEl.style.display = 'none';
        }
    };
}
// ========== UPLOAD FILE ICON CHAT ========== //
const fileInput = document.getElementById('file-input');
const chatInput = document.getElementById('chat-input');

if (fileInput) {
    fileInput.addEventListener('change', async function(e) {
        const file = fileInput.files[0];
        if (!file) return;

        // Client-side validation
        const allowedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 5 * 1024 * 1024; // 5MB limit
        if (!allowedTypes.includes(file.type)) {
            alert('Chỉ hỗ trợ các định dạng .txt, .pdf, .docx!');
            fileInput.value = '';
            return;
        }
        if (file.size > maxSize) {
            alert(`Kích thước file tối đa là ${maxSize / 1024 / 1024}MB!`);
            fileInput.value = '';
            return;
        }

        // Show loading state
        const attachBtn = document.querySelector('.attach-btn');
        attachBtn.disabled = true;
        attachBtn.style.opacity = '0.5';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_ENDPOINT}/upload`, {
                method: 'POST',
                body: formData
            });

            attachBtn.disabled = false;
            attachBtn.style.opacity = '1';

            if (res.ok) {
                const data = await res.json();
                // Assuming the API returns a message or file content to display in chat
                const reply = data.message || 'Tải file lên thành công!';
                chatHistory.push({ sender: 'bot', text: reply });
                renderChat();
                fileInput.value = '';
            } else {
                const err = await res.json();
                chatHistory.push({ sender: 'bot', text: 'Tải file lên thất bại! ' + (err.error || 'Lỗi không xác định.') });
                renderChat();
                fileInput.value = '';
            }
        } catch (err) {
            chatHistory.push({ sender: 'bot', text: 'Lỗi khi tải file lên: ' + err.message });
            renderChat();
            attachBtn.disabled = false;
            attachBtn.style.opacity = '1';
            fileInput.value = '';
        }
    });
}

// Sau khi gửi tin nhắn đầu tiên, thêm class 'chat-active' vào main-content
const mainContent = document.querySelector('.main-content');
const centerContent = document.getElementById('center-content');
let firstMessageSent = false;

// Tối ưu phím tắt cho chat input
chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});
window.addEventListener('DOMContentLoaded', function() {
    chatInput.focus();
});
chatForm.addEventListener('submit', function(e) {
    setTimeout(() => chatInput.focus(), 100);
}); 
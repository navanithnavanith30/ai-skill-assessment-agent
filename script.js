let sessionId = null;

const jdInput = document.getElementById('jd-input');
const resumeInput = document.getElementById('resume-input');
const startBtn = document.getElementById('start-btn');
const loader = document.getElementById('loader');

const chatHistory = document.getElementById('chat-history');
const chatControls = document.getElementById('chat-controls');
const userMsgInput = document.getElementById('user-msg');
const sendBtn = document.getElementById('send-btn');

const statusDot = document.querySelector('.dot');
const statusText = document.getElementById('status-text');

// Initialize markdown options
if (window.marked) {
    marked.setOptions({
        breaks: true, // translate \n to <br>
        gfm: true     // Github flavored markdown
    });
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function setThinkingState(isThinking, text = "Evaluator Thinking...") {
    if (isThinking) {
        statusDot.classList.add('thinking');
        statusText.innerText = text;
        statusText.style.color = '#f59e0b';
    } else {
        statusDot.classList.remove('thinking');
        statusText.innerText = "Evaluator Ready";
        statusText.style.color = '#e2e8f0';
    }
}

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', role);
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('msg-content', 'markdown-body');
    
    // Parse markdown. If user, just raw text protection.
    if (role === 'ai') {
        contentDiv.innerHTML = window.marked ? marked.parse(content) : content;
    } else {
        // Simple escape for user content
        contentDiv.textContent = content; 
    }

    msgDiv.appendChild(contentDiv);
    chatHistory.appendChild(msgDiv);
    
    // Remove the initial system hint if it exists
    const introMsg = document.querySelector('.intro-msg');
    if (introMsg && role !== 'system') {
        introMsg.remove();
    }
    
    setTimeout(scrollToBottom, 50);
}

// Start Assessment
startBtn.addEventListener('click', async () => {
    const jd = jdInput.value.trim();
    const resume = resumeInput.value.trim();

    if (!jd || !resume) {
        alert("Please provide both Job Description and Resume.");
        return;
    }

    // UI Updates
    startBtn.classList.add('hidden');
    loader.classList.remove('hidden');
    jdInput.disabled = true;
    resumeInput.disabled = true;
    
    appendMessage('system', 'Initializing Profile & Analyzing Requirements...');
    setThinkingState(true, "Parsing Profile...");

    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                job_description: jd, 
                resume: resume 
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || "Server error.");
        }

        sessionId = data.session_id;

        // Display AI initial message
        appendMessage('ai', data.reply);
        
        // Show chat controls
        chatControls.classList.remove('hidden');
        userMsgInput.focus();

    } catch (err) {
        appendMessage('system', '❌ Error: ' + err.message);
        console.error(err);
        // Reset UI on failure
        startBtn.classList.remove('hidden');
        loader.classList.add('hidden');
        jdInput.disabled = false;
        resumeInput.disabled = false;
    } finally {
        setThinkingState(false);
        // ensure loader hides even on success since we hide the button entirely if we want
        loader.classList.add('hidden'); 
    }
});

// Auto-expand textarea
userMsgInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if(this.value === '') { this.style.height = 'auto'; }
});

// Handle Send Message
async function sendMessage() {
    const text = userMsgInput.value.trim();
    if (!text || !sessionId) return;

    // Clear input
    userMsgInput.value = '';
    userMsgInput.style.height = 'auto';

    // Show user msg
    appendMessage('user', text);
    
    setThinkingState(true, "Evaluating response...");
    
    // Disable inputs
    userMsgInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId, 
                message: text 
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || "API Auth/Server error.");
        }

        appendMessage('ai', data.reply);

    } catch (err) {
        appendMessage('system', '❌ Interface Error: ' + err.message);
        console.error(err);
    } finally {
        setThinkingState(false);
        userMsgInput.disabled = false;
        sendBtn.disabled = false;
        userMsgInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);

// Allow Enter to send, Shift+Enter for newline
userMsgInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Document Q&A Chat Interface
// Handles PDF upload, chat interactions, and UI updates

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const pdfInput = document.getElementById('pdfInput');
const chooseFileBtn = document.getElementById('chooseFileBtn');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// State
let documentReady = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // File upload
    chooseFileBtn.addEventListener('click', () => pdfInput.click());
    pdfInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Chat
    sendBtn.addEventListener('click', sendMessage);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendBtn.disabled) {
            sendMessage();
        }
    });
    
    // Example questions click
    document.querySelectorAll('.example-list li').forEach(item => {
        item.addEventListener('click', function() {
            if (documentReady) {
                questionInput.value = this.textContent;
                sendMessage();
            } else {
                showBotMessage('📄 Please upload a PDF document first.');
            }
        });
    });
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        uploadFile(file);
    } else {
        showUploadStatus('error', '❌ Please upload a PDF file');
    }
}

// Upload File to Server
async function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showUploadStatus('error', '❌ Only PDF files are supported');
        return;
    }
    
    const formData = new FormData();
    formData.append('pdf', file);
    
    showUploadStatus('loading', `⏳ Uploading and processing ${file.name}...`);
    updateStatus('processing', 'Processing...');
    
    try {
        const response = await fetch('/upload_pdf', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showUploadStatus('success', `✅ ${data.message}`);
            documentReady = true;
            enableChat();
            updateStatus('active', 'Ready');
            showBotMessage(`📄 Document processed successfully! You can now ask questions about: **${data.filename}**`);
        } else {
            showUploadStatus('error', `❌ ${data.error}`);
            updateStatus('ready', 'Upload failed');
        }
    } catch (error) {
        showUploadStatus('error', '❌ Upload failed. Please try again.');
        updateStatus('ready', 'Error');
        console.error('Upload error:', error);
    }
}

// Upload Status Display
function showUploadStatus(type, message) {
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.textContent = message;
}

// Status Indicator
function updateStatus(state, text) {
    statusText.textContent = text;
    
    if (state === 'active') {
        statusDot.classList.add('active');
    } else {
        statusDot.classList.remove('active');
    }
}

// Enable/Disable Chat
function enableChat() {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    questionInput.focus();
}

function disableChat() {
    questionInput.disabled = true;
    sendBtn.disabled = true;
}

// Send Message
async function sendMessage() {
    const question = questionInput.value.trim();
    
    if (!question) {
        return;
    }
    
    if (!documentReady) {
        showBotMessage('📄 Please upload and process a PDF document first.');
        return;
    }
    
    // Show user message
    showUserMessage(question);
    questionInput.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    // Disable input while processing
    disableChat();
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Show bot response
        showBotMessage(data.answer);
        
    } catch (error) {
        removeTypingIndicator(typingId);
        showBotMessage('❌ Sorry, there was an error processing your question. Please try again.');
        console.error('Query error:', error);
    } finally {
        enableChat();
    }
}

// Display Messages
function showUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showBotMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            ${formatBotMessage(text)}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Typing Indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    return 'typing-indicator';
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Format Bot Message
function formatBotMessage(text) {
    // Convert markdown-style formatting
    let formatted = text;
    
    // Bold (**text**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic (*text*)
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code (`code`)
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Paragraphs
    const paragraphs = formatted.split('<br><br>');
    formatted = paragraphs.map(p => `<p>${p}</p>`).join('');
    
    return formatted;
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-focus input on load
window.addEventListener('load', () => {
    if (!questionInput.disabled) {
        questionInput.focus();
    }
});

// Prevent form submission on Enter
questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.shiftKey) {
        e.preventDefault();
        // Allow shift+enter for new line if we add textarea later
    }
});

// Show loading state on page refresh
window.addEventListener('beforeunload', () => {
    updateStatus('ready', 'Refreshing...');
});

// Handle errors gracefully
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    showBotMessage('⚠️ An unexpected error occurred. Please refresh the page.');
});

// Log initialization
console.log('Document Q&A Chat Interface initialized');
console.log('Ready to accept PDF uploads and questions!');
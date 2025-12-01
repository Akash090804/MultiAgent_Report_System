// frontend/app.js
// Frontend logic for AI Report Generator

const API_BASE = window.location.origin;

// UI Elements
const formSection = document.getElementById('formSection');
const progressSection = document.getElementById('progressSection');
const successSection = document.getElementById('successSection');
const errorSection = document.getElementById('errorSection');

const reportForm = document.getElementById('reportForm');
const progressBar = document.getElementById('progressBar');
const progressPercent = document.getElementById('progressPercent');
const progressStage = document.getElementById('progressStage');
const errorMessage = document.getElementById('errorMessage');

let currentJobId = null;
let pollInterval = null;

// Toggle API key visibility
document.getElementById('toggleApiKey').addEventListener('click', function() {
    const apiKeyInput = document.getElementById('apiKey');
    const icon = this.querySelector('i');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        apiKeyInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
});

// Form submission
reportForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const apiKey = document.getElementById('apiKey').value.trim();
    const topic = document.getElementById('topic').value.trim();
    const description = document.getElementById('description').value.trim();
    const author = document.getElementById('author').value.trim();
    const generatePdf = document.getElementById('generatePdf').checked;
    
    // Validation
    if (!apiKey || apiKey.length < 30) {
        alert('Please enter a valid API key');
        return;
    }
    
    if (!topic || topic.length < 10) {
        alert('Topic must be at least 10 characters');
        return;
    }
    
    // Show progress section
    showSection('progress');
    
    // Start generation
    try {
        const response = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                api_key: apiKey,
                topic: topic,
                description: description || null,
                author: author || null,
                generate_pdf: generatePdf
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to start generation');
        }
        
        currentJobId = data.job_id;
        
        // Start polling for status
        startPolling();
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
});

// Show specific section
function showSection(section) {
    formSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    successSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    if (section === 'form') {
        formSection.classList.remove('hidden');
    } else if (section === 'progress') {
        progressSection.classList.remove('hidden');
    } else if (section === 'success') {
        successSection.classList.remove('hidden');
    } else if (section === 'error') {
        errorSection.classList.remove('hidden');
    }
}

// Start polling for job status
function startPolling() {
    pollInterval = setInterval(checkStatus, 2000); // Poll every 2 seconds
    checkStatus(); // Check immediately
}

// Stop polling
function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Check job status
async function checkStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/status/${currentJobId}`);
        const status = await response.json();
        
        // Update progress
        updateProgress(status);
        
        // Check if complete or failed
        if (status.status === 'completed') {
            stopPolling();
            showSuccess(status);
        } else if (status.status === 'failed') {
            stopPolling();
            showError(status.error || 'Generation failed');
        }
        
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Update progress UI
function updateProgress(status) {
    const progress = status.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressPercent.textContent = progress;
    progressStage.textContent = status.current_stage || 'Processing...';
    
    // Highlight active agent
    const stageMap = {
        'Planning structure': 'planner',
        'Researching content': 'researcher',
        'Writing report': 'writer',
        'Formatting document': 'formatter',
        'Quality check': 'qc'
    };
    
    // Reset all agents
    ['planner', 'researcher', 'writer', 'formatter', 'qc'].forEach(agent => {
        const elem = document.getElementById(`agent-${agent}`);
        const icon = elem.querySelector('i');
        icon.classList.remove('text-blue-600', 'text-green-600');
        icon.classList.add('text-gray-300');
    });
    
    // Highlight current and completed (5 agents: 20%, 40%, 60%, 80%, 100%)
    if (progress >= 20) highlightAgent('planner', progress >= 40);
    if (progress >= 40) highlightAgent('researcher', progress >= 60);
    if (progress >= 60) highlightAgent('writer', progress >= 80);
    if (progress >= 80) highlightAgent('formatter', progress >= 100);
    if (progress >= 90) highlightAgent('qc', progress >= 100);
}

// Highlight agent
function highlightAgent(agent, completed) {
    const elem = document.getElementById(`agent-${agent}`);
    const icon = elem.querySelector('i');
    icon.classList.remove('text-gray-300', 'text-blue-600', 'text-green-600');
    
    if (completed) {
        icon.classList.add('text-green-600');
    } else {
        icon.classList.add('text-blue-600');
    }
}

// Show success
function showSuccess(status) {
    showSection('success');
    
    // Set download URLs
    if (status.pdf_url) {
        const pdfBtn = document.getElementById('downloadPdf');
        pdfBtn.href = `${API_BASE}${status.pdf_url}`;
        pdfBtn.style.display = 'flex';
    } else {
        document.getElementById('downloadPdf').style.display = 'none';
    }
    
    if (status.markdown_url) {
        const mdBtn = document.getElementById('downloadMarkdown');
        mdBtn.href = `${API_BASE}${status.markdown_url}`;
    }
}

// Show error
function showError(message) {
    showSection('error');
    errorMessage.textContent = message;
}

// Generate another report
document.getElementById('generateAnother').addEventListener('click', () => {
    // Reset form
    reportForm.reset();
    document.getElementById('generatePdf').checked = true;
    currentJobId = null;
    
    // Show form
    showSection('form');
});

// Try again button
document.getElementById('tryAgain').addEventListener('click', () => {
    currentJobId = null;
    showSection('form');
});
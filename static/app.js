// French Tutor - Frontend JavaScript
const API_BASE = 'http://localhost:8000';

// App State
const AppState = {
    lessons: [],
    currentLesson: null,
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false
};

// Scenario targets mapping
const SCENARIO_TARGETS = {
    cafe: ['Order a coffee', 'Ask for the bill', 'Request the WiFi password'],
    shop: ['Ask for the price', 'Request a different size', 'Pay for items'],
    restaurant: ['Order a meal', 'Ask for recommendations', 'Request the check'],
    hotel: ['Check in', 'Ask about amenities', 'Request room service']
};

// DOM Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const statusEl = document.getElementById('status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('French Tutor loaded');
    checkHealth();
    loadLessons();
    setupTabs();
    setupSpeaking();
    setupHomework();
    loadProgress();
});

// Health check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            statusEl.textContent = data.api_key_loaded 
                ? '✅ Ready (API key loaded)' 
                : '⚠️ Ready (No API key - AI features disabled)';
            statusEl.style.color = data.api_key_loaded ? '#28a745' : '#ffc107';
        }
    } catch (error) {
        statusEl.textContent = '❌ Server not responding';
        statusEl.style.color = '#dc3545';
        console.error('Health check failed:', error);
    }
}

// Tab switching
function setupTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked
            btn.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Load tab-specific data
            if (tabName === 'progress') {
                loadProgress();
            }
        });
    });
}

// Load lessons
async function loadLessons() {
    const listEl = document.getElementById('lessons-list');
    const selectEl = document.getElementById('lesson-select');
    
    try {
        const response = await fetch(`${API_BASE}/api/lessons`);
        const lessons = await response.json();
        AppState.lessons = lessons;
        
        if (lessons.length === 0) {
            listEl.innerHTML = '<p>No lessons available yet.</p>';
            return;
        }
        
        // Populate lessons list
        listEl.innerHTML = lessons.map(lesson => `
            <div class="lesson-card">
                <h3>${lesson.title}</h3>
                <span class="lesson-badge">${lesson.level}</span>
                <p>${lesson.description}</p>
            </div>
        `).join('');
        
        // Populate homework lesson select
        selectEl.innerHTML = '<option value="">-- Choose a lesson --</option>' +
            lessons.map(lesson => `
                <option value="${lesson.lesson_id}">${lesson.title} (${lesson.level})</option>
            `).join('');
        
    } catch (error) {
        listEl.innerHTML = '<p class="error">Failed to load lessons</p>';
        console.error('Failed to load lessons:', error);
    }
}

// Speaking Practice Setup
function setupSpeaking() {
    const scenarioSelect = document.getElementById('scenario-select');
    const targetsList = document.getElementById('targets-list');
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const recordingStatus = document.getElementById('recording-status');
    
    // Update targets when scenario changes
    scenarioSelect.addEventListener('change', () => {
        const targets = SCENARIO_TARGETS[scenarioSelect.value];
        targetsList.innerHTML = targets.map(t => `<li>${t}</li>`).join('');
    });
    
    // Recording
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            AppState.mediaRecorder = new MediaRecorder(stream);
            AppState.audioChunks = [];
            
            AppState.mediaRecorder.ondataavailable = (event) => {
                AppState.audioChunks.push(event.data);
            };
            
            AppState.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(AppState.audioChunks, { type: 'audio/wav' });
                await processAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            AppState.mediaRecorder.start();
            AppState.isRecording = true;
            recordBtn.disabled = true;
            stopBtn.disabled = false;
            recordingStatus.textContent = '🎤 Recording... speak now!';
            
        } catch (error) {
            alert('Microphone access denied');
            console.error('Recording error:', error);
        }
    }
    
    function stopRecording() {
        if (AppState.mediaRecorder && AppState.isRecording) {
            AppState.mediaRecorder.stop();
            AppState.isRecording = false;
            recordBtn.disabled = false;
            stopBtn.disabled = true;
            recordingStatus.textContent = '⏳ Processing...';
        }
    }
    
    async function processAudio(audioBlob) {
        try {
            // Transcribe audio
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');
            
            const transcribeResponse = await fetch(`${API_BASE}/api/audio/transcribe`, {
                method: 'POST',
                body: formData
            });
            const { transcription } = await transcribeResponse.json();
            
            // Get AI feedback
            const scenario = scenarioSelect.value;
            const targets = SCENARIO_TARGETS[scenario];
            
            const feedbackResponse = await fetch(`${API_BASE}/api/speaking/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario: scenario,
                    targets: targets,
                    transcribed_text: transcription
                })
            });
            const { feedback } = await feedbackResponse.json();
            
            // Display feedback
            document.getElementById('feedback-content').textContent = feedback;
            document.getElementById('feedback-box').style.display = 'block';
            recordingStatus.textContent = '✅ Done!';
            
            // Setup TTS playback
            setupTTSPlayback(feedback);
            
        } catch (error) {
            recordingStatus.textContent = '❌ Error processing audio';
            console.error('Audio processing error:', error);
        }
    }
}

function setupTTSPlayback(text) {
    const playBtn = document.getElementById('play-tts-btn');
    playBtn.onclick = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, lang: 'fr' })
            });
            
            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            const audio = new Audio(audioUrl);
            audio.play();
            
        } catch (error) {
            console.error('TTS error:', error);
        }
    };
}

// Homework Setup
function setupHomework() {
    const form = document.getElementById('homework-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const lessonId = document.getElementById('lesson-select').value;
        const homeworkText = document.getElementById('homework-text').value;
        const audioFile = document.getElementById('audio-file').files[0];
        
        if (!lessonId) {
            alert('Please select a lesson');
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('lesson_id', lessonId);
            formData.append('homework_text', homeworkText);
            if (audioFile) {
                formData.append('audio_file', audioFile);
            }
            
            const response = await fetch(`${API_BASE}/api/homework/submit`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            // Display results
            const resultEl = document.getElementById('homework-result');
            const contentEl = document.getElementById('homework-result-content');
            
            contentEl.innerHTML = `
                <p class="${result.passed ? 'success' : 'warning'}">
                    ${result.passed ? '✅ Passed!' : '⚠️ Needs improvement'}
                </p>
                <p><strong>Text Score:</strong> ${result.text_score}%</p>
                ${result.audio_score ? `<p><strong>Audio Score:</strong> ${result.audio_score}%</p>` : ''}
                <p>${result.message}</p>
            `;
            
            resultEl.style.display = 'block';
            form.reset();
            
        } catch (error) {
            alert('Failed to submit homework');
            console.error('Homework submission error:', error);
        }
    });
}

// Load Progress
async function loadProgress() {
    const contentEl = document.getElementById('progress-content');
    
    try {
        const response = await fetch(`${API_BASE}/api/progress/1`);
        const data = await response.json();
        
        if (data.progress && data.progress.length > 0) {
            const progressData = data.progress;
            contentEl.innerHTML = `
                <h3>Lessons Completed</h3>
                <ul>
                    ${progressData.map(p => `
                        <li>
                            <strong>Lesson ${p.lesson_id}</strong> - 
                            Status: ${p.status} 
                            (${p.completion_percentage}% complete)
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            contentEl.innerHTML = '<p>No progress yet. Start your first lesson!</p>';
        }
        
    } catch (error) {
        contentEl.innerHTML = '<p class="error">Failed to load progress</p>';
        console.error('Progress load error:', error);
    }
}

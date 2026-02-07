// French Tutor - Frontend JavaScript
const API_BASE = 'http://localhost:8000';

// App State
const AppState = {
    lessons: [],
    currentLesson: null,
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false,
    vocabMode: 'daily',
    vocabItems: [],
    currentVocabIndex: 0,
    currentVocabItem: null,
    isDevMode: false,
    startingLevel: null,
    currentLevel: null,
    isWaitingForLevel: false
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

function formatDateShort(isoString) {
    if (!isoString) {
        return 'N/A';
    }
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return 'N/A';
    }
    return date.toLocaleDateString();
}

function toDateKey(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('French Tutor loaded');
    (async () => {
        await initializeAppMode();
        checkHealth();
        setupTabs();
        setupSpeaking();
        setupHomework();
        setupVocabulary();
        loadProgress();
        if (!AppState.isWaitingForLevel) {
            loadLessons();
        }
    })();
});

// Health check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            const statusText = data.api_key_loaded 
                ? '✅ Ready (API key loaded)' 
                : '⚠️ Ready (No API key - AI features disabled)';
            statusEl.textContent = statusText;
            statusEl.style.color = data.api_key_loaded ? '#28a745' : '#ffc107';
            
            // Also update the status indicator
            const indicatorEl = document.getElementById('status-indicator');
            if (indicatorEl) {
                indicatorEl.textContent = statusText;
            }
        }
    } catch (error) {
        statusEl.textContent = '❌ Server not responding';
        statusEl.style.color = '#dc3545';
        const indicatorEl = document.getElementById('status-indicator');
        if (indicatorEl) {
            indicatorEl.textContent = '❌ Server not responding';
        }
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
            } else if (tabName === 'vocabulary') {
                loadVocabStats();
            } else if (tabName === 'curriculum') {
                loadCurriculumDashboard();
            }
        });
    });
}

// Load lessons
async function loadLessons() {
    const listEl = document.getElementById('lessons-list');
    const selectEl = document.getElementById('lesson-select');
    
    try {
        const response = await fetch(`${API_BASE}/api/lessons/available`);
        const data = await response.json();
        const lessons = Array.isArray(data) ? data : (data.lessons || []);
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
                <button class="btn-review" data-lesson-id="${lesson.lesson_id}">🔄 Review Lesson</button>
            </div>
        `).join('');
        
        // Add click handlers for review buttons
        document.querySelectorAll('.btn-review').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lessonId = e.target.dataset.lessonId;
                reviewLesson(lessonId);
            });
        });
        
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

async function initializeAppMode() {
    const params = new URLSearchParams(window.location.search);
    const hasDevParam = params.has('dev');
    const devParam = params.get('dev') === 'true';

    if (hasDevParam) {
        await setDevMode(devParam);
    }

    const modeData = await getAppMode();
    AppState.isDevMode = modeData.mode === 'dev';
    AppState.startingLevel = modeData.starting_level || null;
    AppState.currentLevel = modeData.current_level || modeData.starting_level || null;

    updateDevBadge(AppState.isDevMode);

    if (!AppState.isDevMode && !AppState.startingLevel) {
        AppState.isWaitingForLevel = true;
        showFirstTimeModal();
    }
}

async function getAppMode() {
    try {
        const response = await fetch(`${API_BASE}/api/mode`);
        return await response.json();
    } catch (error) {
        console.error('Failed to load app mode:', error);
        return { mode: 'production' };
    }
}

async function setDevMode(enable) {
    try {
        const response = await fetch(`${API_BASE}/api/mode/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dev_mode: Boolean(enable) })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to toggle dev mode:', error);
        return null;
    }
}

function updateDevBadge(isDev) {
    const badge = document.getElementById('dev-badge');
    if (!badge) {
        return;
    }
    badge.style.display = isDev ? 'inline-block' : 'none';
}

function showFirstTimeModal() {
    const modal = document.getElementById('first-time-modal');
    const levelButtons = modal ? modal.querySelectorAll('.level-btn') : [];

    if (!modal || levelButtons.length === 0) {
        return;
    }

    modal.style.display = 'flex';

    levelButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const level = btn.dataset.level;
            if (!level) {
                return;
            }
            await selectStartingLevel(level);
        });
    });
}

async function selectStartingLevel(level) {
    try {
        const response = await fetch(`${API_BASE}/api/first-time-setup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ starting_level: level })
        });
        const data = await response.json();
        AppState.startingLevel = data.starting_level || level;
        AppState.currentLevel = data.current_level || level;
        AppState.isWaitingForLevel = false;

        const modal = document.getElementById('first-time-modal');
        if (modal) {
            modal.style.display = 'none';
        }

        loadLessons();
    } catch (error) {
        console.error('Failed to set starting level:', error);
    }
}

// Speaking Practice Setup
function setupSpeaking() {
    const scenarioSelect = document.getElementById('scenario-select');
    const targetsList = document.getElementById('targets-list');
    const pttBtn = document.getElementById('ptt-btn');
    const recordingStatus = document.getElementById('recording-status');
    let audioStream = null;
    
    // Update targets when scenario changes
    scenarioSelect.addEventListener('change', () => {
        const targets = SCENARIO_TARGETS[scenarioSelect.value];
        targetsList.innerHTML = targets.map(t => `<li>${t}</li>`).join('');
    });
    
    // Push-to-Talk: Mouse events
    pttBtn.addEventListener('mousedown', startRecording);
    document.addEventListener('mouseup', stopRecording);
    
    // Push-to-Talk: Keyboard events (spacebar)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && !AppState.isRecording) {
            e.preventDefault();
            startRecording();
        }
    });
    
    document.addEventListener('keyup', (e) => {
        if (e.code === 'Space' && AppState.isRecording) {
            e.preventDefault();
            stopRecording();
        }
    });
    
    async function startRecording() {
        if (AppState.isRecording) return; // Prevent multiple simultaneous recordings
        
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            AppState.mediaRecorder = new MediaRecorder(audioStream);
            AppState.audioChunks = [];
            
            AppState.mediaRecorder.ondataavailable = (event) => {
                AppState.audioChunks.push(event.data);
            };
            
            AppState.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(AppState.audioChunks, { type: 'audio/wav' });
                await processAudio(audioBlob);
                audioStream.getTracks().forEach(track => track.stop());
                audioStream = null;
            };
            
            AppState.mediaRecorder.start();
            AppState.isRecording = true;
            pttBtn.classList.add('active');
            recordingStatus.textContent = '🎤 Recording... speak now!';
            recordingStatus.style.display = 'block';
            
        } catch (error) {
            alert('Microphone access denied');
            console.error('Recording error:', error);
            AppState.isRecording = false;
        }
    }
    
    function stopRecording() {
        if (AppState.mediaRecorder && AppState.isRecording) {
            AppState.mediaRecorder.stop();
            AppState.isRecording = false;
            pttBtn.classList.remove('active');
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
        
    } catch (error){
        contentEl.innerHTML = '<p class="error">Failed to load progress</p>';
        console.error('Progress load error:', error);
    }
}

// Vocabulary Practice Functions
function setupVocabulary() {
    // Mode buttons
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AppState.vocabMode = btn.dataset.mode;
            loadVocabStats();
        });
    });

    // Start practice button
    document.getElementById('start-vocab-practice').addEventListener('click', startVocabPractice);
    
    // Submit answer button
    document.getElementById('vocab-submit-btn').addEventListener('click', submitVocabAnswer);
    
    // Next question button
    document.getElementById('vocab-next-btn').addEventListener('click', nextVocabQuestion);
    
    // End practice button
    document.getElementById('vocab-end-btn').addEventListener('click', endVocabPractice);

    // TTS button
    document.getElementById('vocab-tts-btn').addEventListener('click', playVocabTTS);
}

async function loadVocabStats() {
    const statsEl = document.getElementById('vocab-stats');
    
    try {
        const response = await fetch(`${API_BASE}/api/vocabulary/stats`);
        const stats = await response.json();

        const levels = Object.entries(stats.vocab_by_level || {})
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([level, count]) => `${level}: ${count}`)
            .join(' | ');

        const weakTopics = (stats.weak_topics || [])
            .map(t => `<li>${t.topic} (${t.accuracy_percentage}%)</li>`)
            .join('') || '<li>No weaknesses tracked yet</li>';

        const weeks = Object.entries(stats.vocab_by_week || {})
            .sort((a, b) => Number(a[0]) - Number(b[0]))
            .slice(-6)
            .map(([week, count]) => `<li>Week ${week}: ${count} words</li>`)
            .join('') || '<li>No weekly data</li>';
        
        statsEl.innerHTML = `
            <div class="stat-box">
                <h4>📊 Vocabulary Dashboard${levels ? ` (${levels})` : ''}</h4>
                <p><strong>Total Vocabulary:</strong> ${stats.total_vocab}</p>
                <p><strong>Lessons With Vocabulary:</strong> ${stats.lessons_with_vocab}</p>
                <p><strong>Due Today:</strong> ${stats.due_today}</p>
                <p><strong>Average Ease:</strong> ${stats.average_ease}</p>
                <p><strong>Avg Interval:</strong> ${stats.average_interval_days.toFixed(1)} days</p>
                <p><strong>Avg Words/Week:</strong> ${stats.average_vocab_per_week}</p>
            </div>
            <div class="stat-box">
                <h4>⚠️ Weak Topics</h4>
                <ul>${weakTopics}</ul>
            </div>
            <div class="stat-box">
                <h4>📈 Recent Weeks</h4>
                <ul>${weeks}</ul>
            </div>
        `;
    } catch (error) {
        statsEl.innerHTML = '<p class="error">Failed to load statistics</p>';
        console.error('Vocab stats error:', error);
    }
}

async function startVocabPractice() {
    const mode = AppState.vocabMode;
    const practiceArea = document.getElementById('vocab-practice-area');
    const startBtn = document.getElementById('start-vocab-practice');
    const statsEl = document.getElementById('vocab-stats');
    
    try {
        // Fetch vocabulary items based on mode
        let endpoint = `/api/vocabulary/practice?mode=${mode}&limit=10`;
        
        const response = await fetch(`${API_BASE}${endpoint}`);
        const data = await response.json();
        
        AppState.vocabItems = data.questions || [];
        
        if (AppState.vocabItems.length === 0) {
            alert('No vocabulary items available for this mode!');
            return;
        }
        
        AppState.currentVocabIndex = 0;
        startBtn.style.display = 'none';
        statsEl.style.display = 'none';
        practiceArea.style.display = 'block';
        
        showVocabQuestion();
        
    } catch (error) {
        alert('Failed to start practice');
        console.error('Vocab practice error:', error);
    }
}

function showVocabQuestion() {
    const item = AppState.vocabItems[AppState.currentVocabIndex];
    AppState.currentVocabItem = item;
    
    const questionEl = document.getElementById('vocab-question');
    const optionsEl = document.getElementById('vocab-options');
    const inputEl = document.getElementById('vocab-answer-input');
    const feedbackEl = document.getElementById('vocab-feedback');
    const submitBtn = document.getElementById('vocab-submit-btn');
    const srsInfoEl = document.getElementById('srs-info');
    const progressEl = document.getElementById('vocab-progress-text');
    const ttsBtn = document.getElementById('vocab-tts-btn');
    const ttsPlayer = document.getElementById('vocab-tts-player');
    
    // Hide feedback, show submit button
    feedbackEl.style.display = 'none';
    submitBtn.parentElement.style.display = 'block';
    
    // Update progress
    progressEl.textContent = `Question ${AppState.currentVocabIndex + 1}/${AppState.vocabItems.length}`;
    
    // Display question
    questionEl.textContent = item.question || item.lesson_id || 'Vocabulary Question';

    if (AppState.vocabMode === 'daily' && item.srs_meta) {
        const dueDate = formatDateShort(item.srs_meta.next_review_date);
        const intervalDays = item.srs_meta.interval_days ?? 'N/A';
        const reps = item.srs_meta.repetitions ?? 0;
        srsInfoEl.textContent = `SRS: Due ${dueDate} | Interval ${intervalDays}d | Reps ${reps}`;
        srsInfoEl.style.display = 'inline-block';
    } else {
        srsInfoEl.textContent = '';
        srsInfoEl.style.display = 'none';
    }

    if (item.french_word) {
        ttsBtn.style.display = 'inline-block';
        ttsBtn.dataset.ttsText = item.french_word;
    } else {
        ttsBtn.style.display = 'none';
        ttsBtn.dataset.ttsText = '';
    }

    ttsPlayer.pause();
    ttsPlayer.removeAttribute('src');
    ttsPlayer.style.display = 'none';
    
    // Check if item has options (MCQ) or requires text input
    if (item.options && item.options.length > 0) {
        inputEl.style.display = 'none';
        optionsEl.style.display = 'block';
        optionsEl.innerHTML = item.options.map((opt, idx) => `
            <label class="vocab-option">
                <input type="radio" name="vocab-answer" value="${opt}">
                ${opt}
            </label>
        `).join('');
    } else {
        optionsEl.style.display = 'none';
        inputEl.style.display = 'block';
        inputEl.value = '';
    }
}

async function playVocabTTS() {
    const ttsBtn = document.getElementById('vocab-tts-btn');
    const ttsPlayer = document.getElementById('vocab-tts-player');
    const text = ttsBtn.dataset.ttsText || '';
    if (!text) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, lang: 'fr' })
        });

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        ttsPlayer.src = audioUrl;
        ttsPlayer.style.display = 'block';
        ttsPlayer.play();
    } catch (error) {
        console.error('Vocab TTS error:', error);
    }
}

function submitVocabAnswer() {
    const inputEl = document.getElementById('vocab-answer-input');
    const optionsEl = document.getElementById('vocab-options');
    const feedbackEl = document.getElementById('vocab-feedback');
    const feedbackTextEl = document.getElementById('vocab-feedback-text');
    
    let userAnswer = '';
    
    // Get answer from radio buttons or text input
    const selectedRadio = document.querySelector('input[name="vocab-answer"]:checked');
    if (selectedRadio) {
        userAnswer = selectedRadio.value;
    } else if (inputEl.style.display !== 'none') {
        userAnswer = inputEl.value.trim();
    }
    
    if (!userAnswer) {
        alert('Please provide an answer!');
        return;
    }
    
    // Submit answer to backend and get feedback
    submitVocabAnswerToBackend(userAnswer);
}

async function submitVocabAnswerToBackend(userAnswer) {
    const item = AppState.currentVocabItem;
    const feedbackEl = document.getElementById('vocab-feedback');
    const feedbackTextEl = document.getElementById('vocab-feedback-text');
    
    try {
        // If SRS item (daily mode), update SRS
        if (AppState.vocabMode === 'daily' && item.srs_id) {
            // For SRS, we need to determine quality (0-5)
            // Simple: if answer is correct, quality=4, else quality=1
            const quality = userAnswer.toLowerCase() === (item.correct_answer || '').toLowerCase() ? 4 : 1;
            
            const response = await fetch(`${API_BASE}/api/srs/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    srs_id: item.srs_id,
                    quality: quality,
                    user_id: 1
                })
            });
            
            const result = await response.json();

            const prevInterval = item.srs_meta ? item.srs_meta.interval_days : null;
            const prevEase = item.srs_meta ? item.srs_meta.ease_factor : null;
            const nextDate = formatDateShort(result.updated_item.next_review_date);
            const intervalText = prevInterval !== null
                ? `${prevInterval}d to ${result.updated_item.interval_days}d`
                : `${result.updated_item.interval_days}d`;
            const easeText = prevEase !== null
                ? `${prevEase.toFixed(2)} to ${result.updated_item.ease_factor.toFixed(2)}`
                : `${result.updated_item.ease_factor.toFixed(2)}`;

            feedbackTextEl.innerHTML = quality >= 3
                ? `✅ Correct! Interval: ${intervalText}. Ease: ${easeText}. Next review: ${nextDate}.`
                : `❌ Incorrect. Interval reset to ${result.updated_item.interval_days}d. Next review: ${nextDate}.`;
        } else {
            // For other modes, just check answer
            const response = await fetch(`${API_BASE}/api/vocabulary/check`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question_id: item.question_id || item.lesson_id,
                    user_answer: userAnswer
                })
            });
            
            const result = await response.json();
            
            // Clean up feedback: remove redundant symbols and text from AI
            let cleanedFeedback = result.feedback || '';
            // Remove leading ✓ or ✗ symbol
            cleanedFeedback = cleanedFeedback.replace(/^[✓✗]\s+/, '').trim();
            // Remove "Correct!" or "Incorrect." at the start if present
            cleanedFeedback = cleanedFeedback.replace(/^(Correct!|Incorrect\.)\s+/, '').trim();
            
            feedbackTextEl.innerHTML = result.correct 
                ? `✅ ${cleanedFeedback || 'Correct!'}`
                : `❌ ${cleanedFeedback || 'Try again'}`;
        }
        
        feedbackEl.style.display = 'block';
        
    } catch (error) {
        feedbackTextEl.textContent = '❌ Error checking answer';
        feedbackEl.style.display = 'block';
        console.error('Vocab answer error:', error);
    }
}

async function loadCurriculumDashboard() {
    const planEl = document.getElementById('curriculum-plan');
    const summaryEl = document.getElementById('srs-summary');
    const dueEl = document.getElementById('srs-due-list');
    const scheduleEl = document.getElementById('srs-schedule');

    if (planEl) {
        planEl.textContent = 'Loading curriculum...';
    }
    summaryEl.textContent = 'Loading curriculum summary...';
    dueEl.textContent = 'Loading due items...';
    scheduleEl.textContent = 'Loading schedule...';

    try {
        const [planResponse, statsResponse, itemsResponse] = await Promise.all([
            fetch(`${API_BASE}/api/curriculum/plan`),
            fetch(`${API_BASE}/api/srs/stats`),
            fetch(`${API_BASE}/api/srs/items`)
        ]);

        const planData = await planResponse.json();
        if (planEl) {
            planEl.textContent = planData.plan || 'Curriculum plan unavailable.';
        }

        const stats = await statsResponse.json();
        const itemsData = await itemsResponse.json();
        const items = itemsData.items || [];

        summaryEl.innerHTML = `
            <strong>Total Items:</strong> ${stats.total_items} | 
            <strong>Due Today:</strong> ${stats.due_today} | 
            <strong>Average Ease:</strong> ${stats.average_ease} | 
            <strong>Avg Interval:</strong> ${stats.average_interval_days} days
        `;

        const now = new Date();
        const dueItems = items.filter(item => {
            if (!item.next_review_date) {
                return false;
            }
            return new Date(item.next_review_date) <= now;
        });

        if (dueItems.length === 0) {
            dueEl.innerHTML = '<p class="srs-row-muted">No items due today.</p>';
        } else {
            const dueRows = dueItems.slice(0, 8).map(item => {
                const lessonLabel = [item.level, item.theme].filter(Boolean).join(' - ') || item.lesson_id;
                return `
                    <tr>
                        <td>${lessonLabel}</td>
                        <td>${formatDateShort(item.next_review_date)}</td>
                        <td>${item.interval_days}d</td>
                    </tr>
                `;
            }).join('');

            const extraCount = dueItems.length > 8
                ? `<p class="srs-row-muted">+${dueItems.length - 8} more due items</p>`
                : '';

            dueEl.innerHTML = `
                <table class="srs-table">
                    <thead>
                        <tr>
                            <th>Lesson</th>
                            <th>Due</th>
                            <th>Interval</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dueRows}
                    </tbody>
                </table>
                ${extraCount}
            `;
        }

        const scheduleMap = new Map();
        for (const item of items) {
            if (!item.next_review_date) {
                continue;
            }
            const dateKey = toDateKey(new Date(item.next_review_date));
            scheduleMap.set(dateKey, (scheduleMap.get(dateKey) || 0) + 1);
        }

        const scheduleRows = [];
        for (let i = 0; i < 14; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            const key = toDateKey(date);
            const count = scheduleMap.get(key) || 0;
            const label = date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
            scheduleRows.push(`
                <tr>
                    <td>${label}</td>
                    <td>${count}</td>
                </tr>
            `);
        }

        scheduleEl.innerHTML = `
            <table class="srs-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Items</th>
                    </tr>
                </thead>
                <tbody>
                    ${scheduleRows.join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        if (planEl) {
            planEl.textContent = 'Failed to load curriculum.';
        }
        summaryEl.innerHTML = '<p class="error">Failed to load curriculum summary</p>';
        dueEl.innerHTML = '<p class="error">Failed to load due items</p>';
        scheduleEl.innerHTML = '<p class="error">Failed to load schedule</p>';
        console.error('Curriculum dashboard error:', error);
    }
}

function nextVocabQuestion() {
    AppState.currentVocabIndex++;
    
    if (AppState.currentVocabIndex >= AppState.vocabItems.length) {
        // Reload questions for continuous practice
        AppState.currentVocabIndex = 0;
        // Optionally refresh items from the server
    }
    
    showVocabQuestion();
}

function endVocabPractice() {
    const practiceArea = document.getElementById('vocab-practice-area');
    const startBtn = document.getElementById('start-vocab-practice');
    const statsEl = document.getElementById('vocab-stats');
    
    practiceArea.style.display = 'none';
    statsEl.style.display = 'block';
    startBtn.style.display = 'block';
    loadVocabStats();
}

// Review Lesson Function
async function reviewLesson(lessonId) {
    try {
        const response = await fetch(`${API_BASE}/api/lessons/${lessonId}/review`, {
            method: 'POST'
        });
        
        const lesson = await response.json();
        
        if (lesson.error) {
            alert(`Error: ${lesson.error}`);
            return;
        }
        
        // Display lesson in a modal or alert (simple version)
        const content = `
📚 **${lesson.title}** (${lesson.level})

**Grammar:**
${lesson.content.grammar.explanation || 'No explanation'}

**New Examples:**
${(lesson.content.grammar.examples || []).map((ex, i) => `${i + 1}. ${ex}`).join('\n')}

**Vocabulary:**
${(lesson.content.vocabulary || []).join(', ')}

This is a review - no homework or exam required!
        `;
        
        alert(content);
        
    } catch (error) {
        alert('Failed to load lesson review');
        console.error('Review lesson error:', error);
    }
}

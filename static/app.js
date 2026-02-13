// French Tutor - Frontend JavaScript
// Use current page origin so API works on any port (8000, 8001, etc.)
const API_BASE = (typeof window !== 'undefined' && window.location?.origin) ? window.location.origin : 'http://localhost:8000';

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
    isWaitingForLevel: false,
    returnLessonModal: null,
    lessonScenarioPrompt: '',
    lessonScenarioTargets: [],
    lastAudioBlob: null,
    lastAudioText: ''
};

// Scenario targets mapping
const SCENARIO_TARGETS = {
    cafe: ['Order a coffee', 'Ask for the bill', 'Request the WiFi password'],
    shop: ['Ask for the price', 'Request a different size', 'Pay for items'],
    restaurant: ['Order a meal', 'Ask for recommendations', 'Request the check'],
    hotel: ['Check in', 'Ask about amenities', 'Request room service'],
    lesson: []
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
    // Delegated click for TTS buttons using data-tts-text (avoids onclick with quotes that can truncate content)
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-tts-inline, .btn-listen-inline');
        if (!btn) return;
        const text = btn.getAttribute('data-tts-text');
        if (text != null) {
            e.preventDefault();
            e.stopPropagation();
            playLessonTTS(text);
        }
    });
    try {
        (async () => {
            try { await initializeAppMode(); } catch (e) { console.error('initializeAppMode error:', e); }
            try { checkHealth(); } catch (e) { console.error('checkHealth error:', e); }
            try { setupTabs(); } catch (e) { console.error('setupTabs error:', e); }
            try { setupSpeaking(); } catch (e) { console.error('setupSpeaking error:', e); }
            try { setupHomework(); } catch (e) { console.error('setupHomework error:', e); }
            try { setupVocabulary(); } catch (e) { console.error('setupVocabulary error:', e); }
            try { setupLessonGeneration(); } catch (e) { console.error('setupLessonGeneration error:', e); }
            try { loadProgress(); } catch (e) { console.error('loadProgress error:', e); }
        })();
    } catch (e) {
        console.error('Error during app initialization:', e);
    }
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
    if (!tabBtns || tabBtns.length === 0) {
        console.warn('Tab buttons not found');
        return;
    }
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            try {
                const tabName = btn.dataset.tab;
                
                // Remove active class from all
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active to clicked
                btn.classList.add('active');
                const tabEl = document.getElementById(`${tabName}-tab`);
                if (tabEl) {
                    tabEl.classList.add('active');
                }
                
                // Load tab-specific data
                if (tabName === 'progress') {
                    loadProgress();
                } else if (tabName === 'vocabulary') {
                    loadVocabStats();
                } else if (tabName === 'curriculum') {
                    loadCurriculumDashboard();
                } else if (tabName === 'lessons') {
                    setupLessonGeneration();
                } else if (tabName === 'speaking') {
                    applyLessonScenarioToSpeakingTab();
                    // Trigger auto-generation of scenario for speaking tab
                    const generateBtn = document.getElementById('generate-scenario-btn');
                    if (generateBtn && !AppState.currentScenario) {
                        // Auto-generate if no scenario yet
                        setTimeout(() => {
                            const event = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            generateBtn.dispatchEvent(event);
                        }, 100);
                    }
                }
            } catch (e) {
                console.error('Error in tab setup:', e);
            }
        });
    });
}

// Setup lesson generation UI and functionality
async function setupLessonGeneration() {
    const weekSelect = document.getElementById('week-select');
    const dayBtns = document.querySelectorAll('.day-btn');
    const generateBtn = document.getElementById('generate-lesson-btn');
    const statusMsg = document.getElementById('lesson-status');
    const selectedDayDisplay = document.getElementById('selected-day-display');
    
    // Guard: if elements don't exist, exit gracefully
    if (!weekSelect || !dayBtns.length || !generateBtn || !statusMsg || !selectedDayDisplay) {
        console.warn('Lesson generation UI elements not found, skipping setup');
        return;
    }
    
    let selectedWeek = null;
    let selectedDay = 1; // Default to day 1
    
    // Populate week select with all 52 weeks
    let weekOptions = '<option value="">-- Choose a week --</option>';
    for (let i = 1; i <= 52; i++) {
        weekOptions += `<option value="${i}">Week ${i}</option>`;
    }
    weekSelect.innerHTML = weekOptions;
    
    // Week select handler
    weekSelect.addEventListener('change', (e) => {
        selectedWeek = parseInt(e.target.value) || null;
        updateGenerateButton();
    });
    
    // Day buttons handler
    dayBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active class from all day buttons
            dayBtns.forEach(b => b.classList.remove('active'));
            // Add active to clicked
            btn.classList.add('active');
            selectedDay = parseInt(btn.dataset.day);
            selectedDayDisplay.textContent = `Selected: Day ${selectedDay}`;
            updateGenerateButton();
        });
    });
    
    // Set first day as default
    dayBtns[0].classList.add('active');
    selectedDayDisplay.textContent = 'Selected: Day 1';
    
    function updateGenerateButton() {
        if (selectedWeek && selectedDay) {
            generateBtn.style.display = 'block';
        } else {
            generateBtn.style.display = 'none';
        }
    }
    
    // Generate button handler
    generateBtn.addEventListener('click', async () => {
        try {
            statusMsg.textContent = 'Loading lesson from curriculum...';
            statusMsg.classList.add('loading');
            statusMsg.style.display = 'block';
            
            const weekValue = parseInt(selectedWeek, 10);
            const dayValue = parseInt(selectedDay, 10);
            const levelValue = AppState.currentLevel || 'A1.1';

            if (Number.isNaN(weekValue) || Number.isNaN(dayValue)) {
                throw new Error('Please select a valid week and day.');
            }
            
            // Use NEW CURRICULUM SYSTEM endpoint: /api/lessons/load
            const response = await fetch(`${API_BASE}/api/lessons/load`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    week: weekValue,
                    day: dayValue,
                    user_id: 1
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.lesson) {
                statusMsg.textContent = '✅ Lesson loaded successfully!';
                statusMsg.classList.remove('loading');
                statusMsg.classList.add('success');
                
                // Store current lesson info for homework
                AppState.currentLesson = {
                    id: data.lesson_id || data.lesson.lesson_id,
                    title: data.lesson.grammar_topic || 'Lesson',
                    week: weekValue,
                    day: dayValue,
                    level: data.lesson.cefr_level,
                    lessonData: data.lesson  // Store full lesson data
                };
                
                // Update homework form
                updateHomeworkLessonDisplay();
                
                displayGeneratedLesson(data.lesson);
            } else {
                throw new Error(data.detail || 'Unknown error');
            }
        } catch (error) {
            statusMsg.textContent = `❌ Error: ${error.message}`;
            statusMsg.classList.remove('loading');
            statusMsg.classList.add('error');
            console.error('Failed to generate lesson:', error);
        }
    });
}

function displayGeneratedLesson(lesson) {
    // NEW CURRICULUM SYSTEM - Use redesigned format
    // lesson.content.grammar: object with explanation property
    // lesson.content.vocabulary: array of {word, type, english, pronunciation, example}
    // lesson.content.quiz: object with questions property
    
    // Check if this is the NEW modular API format
    const isModularFormat = lesson.content && lesson.content.grammar && typeof lesson.content.grammar === 'object';
    
    if (isModularFormat) {
        // MODULAR FORMAT (from refactored API with curriculum parser)
        const grammarData = lesson.content.grammar || {};
        const vocabItems = (lesson.content.vocabulary || []).map(item => ({
            front: item.word || '',
            back: item.english || '',
            pronunciation: item.pronunciation || '',
            example: item.example || '',
            type: item.type || ''
        }));
        
        const speakingData = lesson.content.speaking || {};
        const quizData = lesson.content.quiz || {};

        const interactiveLesson = {
            title: lesson.title || 'Lesson',
            level: lesson.level || 'A1.1',
            content: {
                grammar: {
                    explanation: grammarData.explanation || '',
                    full_section: grammarData.full_section || '',
                    examples: grammarData.examples || []
                },
                vocabulary: vocabItems,
                speaking: {
                    prompt: speakingData.prompt || '',
                    targets: speakingData.scenario ? [speakingData.scenario] : [],
                    scenario: speakingData.scenario || ''
                },
                quiz: quizData
            }
        };
        
        // Create and display interactive modal
        const modal = createLessonModal(interactiveLesson);
        document.body.appendChild(modal);
        
    } else if (lesson.grammar_explanation && typeof lesson.grammar_explanation === 'string') {
        // OLD NEW FORMAT (grammar_explanation as string)
        // NEW FORMAT (Research/NEW_CURRICULUM_REDESIGNED/)
        const vocabItems = (lesson.vocabulary || []).map(item => ({
            front: item.word || '',
            back: item.english || '',
            pronunciation: item.pronunciation || '',
            example: item.example || '',
            type: item.type || ''
        }));
        
        const quizQuestions = (lesson.quiz_questions || []).map(q => ({
            ...q,
            content_ids: q.content_identifiers || [],
            question_type: q.question_type || 'unknown'
        }));

        const interactiveLesson = {
            title: lesson.grammar_topic || 'Lesson',
            level: lesson.cefr_level || 'A1.1',
            week: lesson.week,
            day: lesson.day,
            content_identifiers: lesson.content_identifiers || [],
            speaking_tier: lesson.speaking_tier || 1,
            content: {
                grammar: {
                    explanation: lesson.grammar_explanation || '',  // Already HTML
                    topic: lesson.grammar_topic || '',
                    examples: [],  // Examples are in quiz_questions
                    conjugation: []
                },
                vocabulary: vocabItems,
                speaking: {
                    prompt: `Speaking practice: ${lesson.grammar_topic}`,
                    targets: [`Use ${lesson.grammar_topic}`, 'Practice pronunciation'],
                    tier: lesson.speaking_tier || 1
                },
                quiz: {
                    questions: quizQuestions,
                    total_available: lesson.total_available_questions || 50,
                    content_identifiers: lesson.content_identifiers || []
                }
            }
        };
        
        // Create and display interactive modal
        const modal = createLessonModal(interactiveLesson);
        document.body.appendChild(modal);
        
    } else {
        // OLD FORMAT (fallback for legacy lessons)
        const grammarExamples = (lesson.grammar?.examples || []).map(ex => {
            if (typeof ex === 'string') {
                return ex;
            }
            if (ex && ex.french && ex.english) {
                return `${ex.french} - ${ex.english}`;
            }
            return String(ex);
        });

        const vocabItems = (lesson.vocabulary?.words || []).map(item => {
            if (typeof item === 'string') {
                return { front: item, back: '', pronunciation: '' };
            }
            return {
                front: item.word || String(item),
                back: item.definition || '',
                pronunciation: item.pronunciation_tip || ''
            };
        });

        const speakingTargets = lesson.speaking?.target_phrases
            || lesson.speaking?.example_interaction
            || (lesson.speaking?.success_criteria ? [lesson.speaking.success_criteria] : []);

        const speakingPrompt = lesson.speaking?.scenario_prompt
            || lesson.speaking?.prompt
            || lesson.speaking?.scenario_domain
            || '';

        AppState.lessonScenarioPrompt = speakingPrompt;
        AppState.lessonScenarioTargets = Array.isArray(speakingTargets) ? speakingTargets : [];
        SCENARIO_TARGETS.lesson = AppState.lessonScenarioTargets;

        const interactiveLesson = {
            title: lesson.theme || 'Lesson',
            level: lesson.level,
            content: {
                grammar: {
                    explanation: lesson.grammar?.explanation || '',
                    examples: grammarExamples,
                    conjugation: lesson.grammar?.conjugation || []
                },
                vocabulary: vocabItems,
                speaking: {
                    prompt: speakingPrompt,
                    targets: Array.isArray(speakingTargets) ? speakingTargets : []
                },
                quiz: lesson.quiz || {}
            }
        };
        
        // Create and display interactive modal
        const modal = createLessonModal(interactiveLesson);
        document.body.appendChild(modal);
    }
}

function updateHomeworkLessonDisplay() {
    const infoEl = document.getElementById('current-lesson-info');
    const lessonSelect = document.getElementById('lesson-select');
    
    if (AppState.currentLesson) {
        infoEl.textContent = `📚 Week ${AppState.currentLesson.week}, Day ${AppState.currentLesson.day} - ${AppState.currentLesson.title} (${AppState.currentLesson.level})`;
        infoEl.style.color = '#28a745';
        lessonSelect.value = AppState.currentLesson.id;
    } else {
        infoEl.textContent = '⚠️ Generate a lesson first in the Lessons tab';
        infoEl.style.color = '#666';
        lessonSelect.value = '';
    }
}

function renderConjugationTable(table) {
    if (!table || !table.rows || table.rows.length === 0) return '';
    
    let html = '<table class="grammar-table"><thead><tr>';
    
    // Add headers
    if (table.headers) {
        table.headers.forEach(h => html += `<th>${h}</th>`);
    }
    html += '</tr></thead><tbody>';
    
    // Add rows
    table.rows.forEach(row => {
        html += '<tr>';
        Object.values(row).forEach(cell => html += `<td>${cell}</td>`);
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

function showSpeakingPractice() {
    if (window.currentLessonModal) {
        AppState.returnLessonModal = window.currentLessonModal;
        window.currentLessonModal.style.display = 'none';
    }

    const lessonSpeaking = window.currentLessonModal?.lesson?.content?.speaking || {};
    const lessonPrompt = lessonSpeaking.prompt || lessonSpeaking.scenario_prompt || lessonSpeaking.scenario_context || lessonSpeaking.scenario_domain || '';
    const lessonTargets = Array.isArray(lessonSpeaking.targets) && lessonSpeaking.targets.length > 0
        ? lessonSpeaking.targets
        : (Array.isArray(lessonSpeaking.target_phrases) ? lessonSpeaking.target_phrases : []);

    AppState.lessonScenarioPrompt = lessonPrompt;
    AppState.lessonScenarioTargets = lessonTargets;
    SCENARIO_TARGETS.lesson = lessonTargets;

    setTimeout(() => {
        const speakingTab = document.querySelector('[data-tab="speaking"]');
        if (speakingTab) {
            speakingTab.click();
        }
        applyLessonScenarioToSpeakingTab();
    }, 100);
}

function applyLessonScenarioToSpeakingTab() {
    const speakingTabContent = document.getElementById('speaking-tab');
    if (!speakingTabContent) {
        return;
    }

    // New design uses auto-generated scenarios, not fixed dropdowns
    // Just make sure return box exists if coming from lesson
    let returnBox = document.getElementById('return-to-lesson');
    if (!returnBox) {
        returnBox = document.createElement('div');
        returnBox.id = 'return-to-lesson';
        returnBox.className = 'return-to-lesson';
        returnBox.innerHTML = `
            <button class="btn-secondary" type="button">← Return to Lesson</button>
        `;
        const header = speakingTabContent.querySelector('h2');
        header?.insertAdjacentElement('afterend', returnBox);
    }
    returnBox.style.display = AppState.returnLessonModal ? 'block' : 'none';
    returnBox.querySelector('button')?.addEventListener('click', () => {
        if (AppState.returnLessonModal) {
            AppState.returnLessonModal.style.display = 'block';
            AppState.returnLessonModal = null;
        }
        returnBox.style.display = 'none';
    });
}

// Escape HTML so user content cannot break the DOM or truncate at </p>, etc.
function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// Escape for HTML attribute value (avoids truncation when " or ' in text closes attribute).
function escapeAttr(str) {
    if (typeof str !== 'string') return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// Build a paragraph element from text, with TTS buttons for "French" (English) — uses DOM so quotes never break HTML.
function buildGrammarParagraphElement(paragraphText) {
    const p = document.createElement('p');
    const parenGroup = '([^)\\n]+)';
    const quotedPattern = new RegExp(`"([^"]+)"\\s*\\(${parenGroup}\\)`, 'g');
    let lastIndex = 0;
    let match;
    let matchCount = 0;
    while ((match = quotedPattern.exec(paragraphText)) !== null) {
        matchCount++;
        const [full, frenchText, englishTranslation] = match;
        const before = paragraphText.slice(lastIndex, match.index);
        if (before) p.appendChild(document.createTextNode(before));
        const ttsText = frenchText.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').trim();
        p.appendChild(document.createTextNode('"'));
        const strong = document.createElement('strong');
        strong.textContent = frenchText;
        p.appendChild(strong);
        p.appendChild(document.createTextNode('" '));
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-tts-inline';
        btn.setAttribute('data-tts-text', ttsText);
        btn.title = 'Listen to pronunciation';
        btn.textContent = '🔊';
        p.appendChild(btn);
        p.appendChild(document.createTextNode(' '));
        const span = document.createElement('span');
        span.className = 'muted';
        span.textContent = `(${englishTranslation.trim()})`;
        p.appendChild(span);
        lastIndex = quotedPattern.lastIndex;
    }
    // #region agent log
    if (paragraphText.indexOf('Cultural Note') !== -1) {
        fetch('http://127.0.0.1:7242/ingest/913ece5b-52f2-4152-8429-45481256fffe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:buildGrammarParagraphElement',message:'Cultural Note paragraph',data:{paraLen:paragraphText.length,matchCount,last120:paragraphText.slice(-120)},timestamp:Date.now(),hypothesisId:'C'})}).catch(()=>{});
    }
    // #endregion
    if (lastIndex < paragraphText.length) {
        p.appendChild(document.createTextNode(paragraphText.slice(lastIndex)));
    }
    return p;
}

function addTTSButtonsToExamples(text) {
    try {
        // Track which parts have already been processed to avoid duplicate buttons
        let processedText = text;
        
        // Parenthetical capture must NOT match newlines, or we eat content up to a later )
        const parenGroup = '([^)\\n]+)';
        
        // Pattern 1: Dialogue format - A: "French" (English) or - A: "French" (English)
        // Example: A: "C'est un stylo bleu." (It's a blue pen. - M)
        const dialoguePattern = new RegExp(`(-?\\s*[A-Z]:\\s*)"([^"]+)"\\s*\\(${parenGroup}\\)`, 'g');
        processedText = processedText.replace(dialoguePattern, (match, prefix, frenchText, englishTranslation) => {
            const ttsText = frenchText.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').trim();
            const safeFrench = escapeHtml(frenchText);
            const safeEnglish = escapeHtml(englishTranslation.trim());
            return `${prefix}"<strong>${safeFrench}</strong>" <button type="button" class="btn-tts-inline" data-tts-text="${escapeAttr(ttsText)}" title="Listen to pronunciation">🔊</button> <span class="muted">(${safeEnglish})</span>`;
        });
        
        // Pattern 2: Arrow format - text → French sentence (English translation)
        // Example: "Parler (to speak) → J'ai parlé français. (I spoke French.)"
        const arrowPattern = new RegExp(`([^→\\n]+)→\\s*([^(]+)\\s*\\(${parenGroup}\\)`, 'g');
        processedText = processedText.replace(arrowPattern, (match, before, frenchSentence, englishTranslation) => {
            const french = frenchSentence.trim();
            const ttsText = french.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').trim();
            const safeFrench = escapeHtml(french);
            const safeEnglish = escapeHtml(englishTranslation.trim());
            return `${before.trim()} → <strong>${safeFrench}</strong> <button type="button" class="btn-tts-inline" data-tts-text="${escapeAttr(ttsText)}" title="Listen to pronunciation">🔊</button> <span class="muted">(${safeEnglish})</span>`;
        });
        
        // Pattern 3: Quoted French text - "French text" (English translation)
        // But only if not already processed by dialogue pattern
        const quotedPattern = new RegExp(`"([^"]+)"\\s*\\(${parenGroup}\\)`, 'g');
        const alreadyProcessed = new Set();
        processedText = processedText.replace(quotedPattern, (match, frenchText, englishTranslation) => {
            // Skip if already has a button next to it
            if (match.includes('<button') || alreadyProcessed.has(match)) {
                return match;
            }
            alreadyProcessed.add(match);
            const ttsText = frenchText.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').trim();
            const safeFrench = escapeHtml(frenchText);
            const safeEnglish = escapeHtml(englishTranslation.trim());
            return `"<strong>${safeFrench}</strong>" <button type="button" class="btn-tts-inline" data-tts-text="${escapeAttr(ttsText)}" title="Listen to pronunciation">🔊</button> <span class="muted">(${safeEnglish})</span>`;
        });
        
        // Pattern 4: Dialogue without parenthetical translation
        // Match lines like: "A: Je m'appelle Marie." or "B: Pourquoi pas?"
        const simpleDialoguePattern = /(-?\s*[A-Z]:\s*)([A-Z][^?\n.!]*[?.!])(?!\s*<button)/g;
        processedText = processedText.replace(simpleDialoguePattern, (match, prefix, frenchSentence) => {
            const ttsText = frenchSentence.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').trim();
            // Only add button if it looks like French
            if (/[àâäçéèêëïîôöûüœæ]|[aeiouy]'|que|pas|pas\?|ne |je |vous |tu /i.test(ttsText)) {
                return `${prefix}<strong>${frenchSentence}</strong> <button type="button" class="btn-tts-inline" data-tts-text="${escapeAttr(ttsText)}" title="Listen to pronunciation">🔊</button>`;
            }
            return match;
        });
        
        return processedText;
    } catch (error) {
        console.error('Error in addTTSButtonsToExamples:', error, 'Input text:', text);
        // Return original text if processing fails
        return text;
    }
}

function playLessonTTS(text) {
    if (!text) {
        return;
    }
    fetch(`${API_BASE}/api/audio/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, lang: 'fr' })
    })
        .then(response => response.blob())
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            const audio = new Audio(audioUrl);
            audio.play();
        })
        .catch(error => console.error('TTS error:', error));
}

function extractQuizAnswerFromText(questionText) {
    if (!questionText) {
        return { cleanText: '', extractedAnswer: '' };
    }

    const separators = ['→', '->', '=>'];
    for (const sep of separators) {
        if (questionText.includes(sep)) {
            const parts = questionText.split(sep);
            const cleanText = parts[0].trim();
            const extractedAnswer = parts.slice(1).join(sep).trim();
            return { cleanText, extractedAnswer };
        }
    }

    return { cleanText: questionText.trim(), extractedAnswer: '' };
}

function extractQuotedText(text) {
    if (!text) {
        return '';
    }
    const match = text.match(/["“”'‘’]([^"“”'‘’]+)["“”'‘’]/);
    return match ? match[1].trim() : '';
}

function getQuizAudioText(questionText, question) {
    if (question && typeof question === 'object') {
        const audioText = question.audio_text || question.listen_text || question.tts_text || '';
        if (audioText) {
            return String(audioText).trim();
        }
    }
    const quoted = extractQuotedText(questionText);
    if (quoted) {
        return quoted;
    }
    return questionText;
}

function normalizeQuizText(text) {
    return String(text)
        .toLowerCase()
        .replace(/[.,!?;:()\[\]{}"'\s]+/g, ' ')
        .trim();
}

function normalizeQuizQuestions(questions) {
    if (!Array.isArray(questions)) {
        return [];
    }

    return questions.map((question, idx) => {
        const normalized = typeof question === 'string'
            ? { id: idx, question: question, options: [] }
            : { ...question };

        const questionText = normalized.question || normalized.question_text || '';
        const { cleanText, extractedAnswer } = extractQuizAnswerFromText(questionText);
        if (cleanText) {
            normalized.question = cleanText;
        }

        const correctAnswerRaw = normalized.correct_answer;
        const hasCorrectAnswer = correctAnswerRaw !== undefined && correctAnswerRaw !== null && String(correctAnswerRaw).trim() !== '';
        if (!hasCorrectAnswer && extractedAnswer) {
            normalized.correct_answer = extractedAnswer;
        }

        if (Array.isArray(normalized.options) && normalized.options.length > 0) {
            const answerValue = normalized.correct_answer;
            const numericAnswer = Number.parseInt(answerValue, 10);
            if (!Number.isNaN(numericAnswer) && numericAnswer >= 0 && numericAnswer < normalized.options.length) {
                normalized.correct_answer = normalized.options[numericAnswer];
            }
        }

        return normalized;
    });
}

function showQuiz() {
    // Interactive quiz is now part of the lesson flow
    // This function is no longer needed
}

function showHomeworkSubmit(lessonId) {
    // Switch to homework tab
    document.querySelector('[data-tab="homework"]').click();
    // Would also set the lesson select if needed
    document.getElementById('lesson-select').value = lessonId;
}

// Load lessons
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
    } catch (error) {
        console.error('Failed to set starting level:', error);
    }
}

// Speaking Practice Setup
function setupSpeaking() {
    const generateBtn = document.getElementById('generate-scenario-btn');
    const tryAnotherBtn = document.getElementById('try-another-btn');
    const scenarioDisplay = document.getElementById('scenario-display');
    const scenarioText = document.getElementById('scenario-text');
    const scenarioLocation = document.getElementById('scenario-location-text');
    const targetsList = document.getElementById('targets-list');
    const targetBox = document.getElementById('targets-box');
    const recordingBox = document.getElementById('recording-box');
    const pttBtn = document.getElementById('ptt-btn');
    const recordingStatus = document.getElementById('recording-status');
    let audioStream = null;
    
    // Guard: if elements don't exist, exit gracefully
    if (!generateBtn || !tryAnotherBtn || !pttBtn || !recordingStatus) {
        console.warn('Speaking practice UI elements not found, skipping setup');
        return;
    }
    
    // Initialize AppState for scenarios
    AppState.currentScenario = null;
    AppState.currentScenarioLocation = null;
    AppState.currentTargets = [];
    
    // Generate scenario button
    generateBtn.addEventListener('click', generateNewScenario);
    tryAnotherBtn.addEventListener('click', generateNewScenario);
    
    async function generateNewScenario() {
        try {
            generateBtn.disabled = true;
            generateBtn.textContent = '⏳ Generating...';
            
            const response = await fetch(`${API_BASE}/api/speaking/random-scenario`);
            const data = await response.json();
            
            if (data.error) {
                alert('Failed to generate scenario: ' + data.error);
                generateBtn.disabled = false;
                generateBtn.textContent = '🎲 Generate Random Scenario';
                return;
            }
            
            // Store current scenario in AppState
            AppState.currentScenario = data.scenario;
            AppState.currentScenarioLocation = data.location;
            
            // Extract target phrases from scenario text (look for numbered items like "1.", "2.", etc.)
            const targetMatches = data.scenario.match(/\d+\.\s+([^:]+):/g);
            AppState.currentTargets = targetMatches
                ? targetMatches.map(t => t.replace(/^\d+\.\s+/, '').replace(/:$/, '').trim())
                : [];
            
            // Display scenario
            scenarioLocation.textContent = data.location;
            scenarioText.textContent = data.scenario;
            scenarioDisplay.style.display = 'block';
            
            // Display targets
            if (AppState.currentTargets.length > 0) {
                targetsList.innerHTML = AppState.currentTargets
                    .map(t => `<li>${t}</li>`)
                    .join('');
                targetBox.style.display = 'block';
            }
            
            // Show recording and try another button
            recordingBox.style.display = 'block';
            tryAnotherBtn.style.display = 'block';
            
            generateBtn.disabled = false;
            generateBtn.textContent = '🎲 Generate Random Scenario';
            recordingStatus.textContent = 'Hold button or press SPACE to record';
            
        } catch (error) {
            alert('Failed to generate scenario: ' + error.message);
            generateBtn.disabled = false;
            generateBtn.textContent = '🎲 Generate Random Scenario';
            console.error('Scenario generation error:', error);
        }
    }
    
    // Push-to-Talk: Mouse events
    pttBtn.addEventListener('mousedown', startRecording);
    document.addEventListener('mouseup', stopRecording);
    
    // Push-to-Talk: Keyboard events (spacebar)
    document.addEventListener('keydown', (e) => {
        if (document.querySelector('.lesson-modal')) {
            return;
        }
        if (e.code === 'Space' && !AppState.isRecording) {
            e.preventDefault();
            startRecording();
        }
    });
    
    document.addEventListener('keyup', (e) => {
        if (document.querySelector('.lesson-modal')) {
            return;
        }
        if (e.code === 'Space' && AppState.isRecording) {
            e.preventDefault();
            stopRecording();
        }
    });
    
    async function startRecording() {
        if (!AppState.currentScenario) {
            alert('Please generate a scenario first');
            return;
        }
        
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
            // Transcribe audio with target phrases as hints
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');
            formData.append('targets', JSON.stringify(AppState.currentTargets));  // Send hints for better accuracy
            
            const transcribeResponse = await fetch(`${API_BASE}/api/audio/transcribe`, {
                method: 'POST',
                body: formData
            });
            const { text: transcription } = await transcribeResponse.json();
            
            // Get AI's response (as conversation partner)
            const feedbackResponse = await fetch(`${API_BASE}/api/speaking/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scenario: AppState.currentScenarioLocation,
                    targets: AppState.currentTargets,
                    transcribed_text: transcription
                })
            });
            const { feedback } = await feedbackResponse.json();
            
            // Display conversation exchange
            const feedbackBox = document.getElementById('feedback-box');
            const feedbackContent = document.getElementById('feedback-content');
            
            feedbackContent.innerHTML = `
                <div class="dialogue-exchange">
                    <div class="dialogue-student">
                        <strong>You:</strong> ${transcription}
                    </div>
                    <div class="dialogue-ai">
                        <strong>AI:</strong> ${feedback}
                    </div>
                </div>
            `;
            feedbackBox.style.display = 'block';
            recordingStatus.textContent = '✅ AI responded!';
            
            // Setup TTS playback for AI's response
            setupTTSPlayback(feedback);
            
        } catch (error) {
            recordingStatus.textContent = '❌ Error processing audio';
            console.error('Audio processing error:', error);
        }
    }
    
    // Auto-generate first scenario when speaking tab is opened
    // (This will be called when setupTabs triggers tab change)
}

function setupTTSPlayback(text) {
    const playBtn = document.getElementById('play-tts-btn');
    
    // Create a function that plays audio (either stored or fetched)
    async function playAudio() {
        try {
            // Check if we have cached audio for this text
            if (!AppState.lastAudioBlob || AppState.lastAudioText !== text) {
                // Fetch fresh audio
                const response = await fetch(`${API_BASE}/api/audio/tts`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, lang: 'fr' })
                });
                
                AppState.lastAudioBlob = await response.blob();
                AppState.lastAudioText = text;
            }
            
            // Play the audio
            const audioUrl = URL.createObjectURL(AppState.lastAudioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
            
        } catch (error) {
            console.error('TTS error:', error);
        }
    }
    
    // Set button to call playAudio function
    playBtn.onclick = playAudio;
    
    // Auto-play immediately
    playAudio();
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
            alert('⚠️ Please generate a lesson first in the Lessons tab');
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
        const response = await fetch(`${API_BASE}/api/audio/tts`, {
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
async function displayLesson(lessonId) {
    try {
        const response = await fetch(`${API_BASE}/api/lessons/${lessonId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const lesson = await response.json();
        AppState.currentLesson = lesson;
        
        // Create and display lesson modal
        const modal = createLessonModal(lesson);
        document.body.appendChild(modal);
        
        // Auto-remove modal when close button clicked
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.remove();
            });
        }
        
    } catch (error) {
        console.error('Failed to load lesson:', error);
        alert(`Failed to load lesson: ${error.message}`);
    }
}

function createLessonModal(lesson) {
    const modal = document.createElement('div');
    modal.className = 'lesson-modal';
    
    // Initialize lesson state
    const lessonState = {
        currentSection: 0, // 0: grammar, 1: vocab, 2: speaking, 3: quiz
        sections: ['grammar', 'vocabulary', 'speaking', 'quiz'],
        sectionProgress: { grammar: false, vocabulary: false, speaking: false, quiz: false },
        quizAnswers: {},
        vocabAnswers: {}
    };
    
    const updateLessonView = () => {
        const section = lessonState.sections[lessonState.currentSection];
        let sectionHTML = '';
        
        switch(section) {
            case 'grammar':
                sectionHTML = createInteractiveGrammar(lesson.content.grammar);
                break;
            case 'vocabulary':
                sectionHTML = createInteractiveVocabulary(lesson.content.vocabulary);
                break;
            case 'speaking':
                sectionHTML = createInteractiveSpeaking(lesson.content.speaking);
                break;
            case 'quiz':
                sectionHTML = createInteractiveQuiz(lesson.content.quiz);
                break;
        }
        
        const progressPercent = Math.round((lessonState.currentSection / 4) * 100);
        
        lessonContent.innerHTML = `
            <div class="lessonflow-header">
                <h3>${lesson.title} - ${section.charAt(0).toUpperCase() + section.slice(1)}</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercent}%"></div>
                </div>
            </div>
            ${sectionHTML}
            <div class="lessonflow-nav">
                <button class="btn-secondary" onclick="lessonGoBack()" ${lessonState.currentSection === 0 ? 'disabled' : ''}>← Back</button>
                <button class="btn-primary" onclick="lessonContinue()">
                    ${lessonState.currentSection === 3 ? 'Finish' : 'Next →'}
                </button>
            </div>
        `;

        if (section === 'speaking') {
            setupEmbeddedSpeaking(lessonContent, lesson.content.speaking);
        }
    };
    
    // Store functions on modal for access
    modal.lessonState = lessonState;
    modal.lesson = lesson;
    modal.updateLessonView = updateLessonView;
    
    modal.innerHTML = `
        <div class="lesson-modal-content lesson-flow-modal">
            <button class="modal-close" aria-label="Close">x</button>
            <div id="lesson-flow-content">
                <!-- Content updated dynamically -->
            </div>
        </div>
    `;
    
    const lessonContent = modal.querySelector('#lesson-flow-content');
    const closeBtn = modal.querySelector('.modal-close');
    
    closeBtn.addEventListener('click', () => modal.remove());
    
    // Make functions available globally for button click handlers
    window.currentLessonModal = modal;
    window.lessonGoBack = () => {
        if (lessonState.currentSection > 0) {
            lessonState.currentSection--;
            updateLessonView();
        }
    };
    window.lessonContinue = () => {
        if (lessonState.currentSection < 3) {
            lessonState.currentSection++;
            updateLessonView();
        } else {
            // Finish lesson
            alert('Lesson completed! 🎉');
            modal.remove();
        }
    };
    
    // Show first section
    updateLessonView();
    return modal;
}

function createSectionHTML(title, content) {
    if (!content || (Array.isArray(content) && content.length === 0)) {
        return '';
    }
    
    let html = `<div class="lesson-section">`;
    html += `<h3>${title}</h3>`;
    
    if (typeof content === 'string') {
        html += `<p>${content}</p>`;
    } else if (Array.isArray(content)) {
        html += `<ul>`;
        content.forEach(item => {
            html += `<li>${item}</li>`;
        });
        html += `</ul>`;
    } else if (typeof content === 'object') {
        // For grammar/speaking objects
        if (content.explanation) {
            html += `<p><strong>Explanation:</strong> ${content.explanation}</p>`;
        }
        if (content.examples && Array.isArray(content.examples)) {
            html += `<p><strong>Examples:</strong></p><ul>`;
            content.examples.forEach(ex => {
                html += `<li>${ex}</li>`;
            });
            html += `</ul>`;
        }
        if (content.prompt) {
            html += `<p><strong>Prompt:</strong> ${content.prompt}</p>`;
        }
        if (content.targets && Array.isArray(content.targets)) {
            html += `<p><strong>Learning Targets:</strong></p><ul>`;
            content.targets.forEach(target => {
                html += `<li>${target}</li>`;
            });
            html += `</ul>`;
        }
    }
    
    html += `</div>`;
    return html;
}

// Interactive sections for lesson flow
function createInteractiveGrammar(grammarContent) {
    let html = '<div class="lesson-section-interactive">';
    html += '<h3>📖 Learn the Grammar Rule</h3>';
    
    let hasContent = false;
    
    // Handle string content
    const renderExplanationParagraphs = (explanationText) => {
        const paragraphs = explanationText.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/913ece5b-52f2-4152-8429-45481256fffe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:renderExplanationParagraphs',message:'explanation received',data:{len:explanationText.length,tail:explanationText.slice(-200),paraCount:paragraphs.length},timestamp:Date.now(),hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        const wrapper = document.createElement('div');
        wrapper.className = 'grammar-explanation';
        paragraphs.forEach(para => {
            wrapper.appendChild(buildGrammarParagraphElement(para));
        });
        const out = wrapper.innerHTML;
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/913ece5b-52f2-4152-8429-45481256fffe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:renderExplanationParagraphs',message:'after innerHTML',data:{serializedLen:out.length,tail:out.slice(-200)},timestamp:Date.now(),hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        return out;
    };
    if (typeof grammarContent === 'string' && grammarContent.trim()) {
        html += renderExplanationParagraphs(grammarContent);
        hasContent = true;
    } else if (typeof grammarContent === 'object' && grammarContent !== null) {
        // Handle object with explanation — use DOM-built paragraphs so quotes never truncate content
        if (grammarContent.explanation && grammarContent.explanation.trim()) {
            html += renderExplanationParagraphs(grammarContent.explanation);
            hasContent = true;
        }
        
        // Handle conjugation array
        if (grammarContent.conjugation && Array.isArray(grammarContent.conjugation) && grammarContent.conjugation.length > 0) {
            html += '<div class="grammar-conjugation">';
            html += '<h4>Conjugation:</h4>';
            html += '<ul>';
            grammarContent.conjugation.forEach(conj => {
                if (conj && typeof conj === 'string') {
                    html += `<li>${conj}</li>`;
                }
            });
            html += '</ul></div>';
            hasContent = true;
        }
        
        // Handle examples array
        if (grammarContent.examples && Array.isArray(grammarContent.examples) && grammarContent.examples.length > 0) {
            html += '<div class="grammar-examples">';
            html += '<h4>Examples:</h4>';
            html += '<ul>';
            grammarContent.examples.forEach(ex => {
                if (!ex) {
                    return;
                }
                if (typeof ex === 'string') {
                    const ttsText = ex.replace(/\([^)]*\)/g, '').replace(/\*\*/g, '').trim();
                    html += `<li><strong>${ex}</strong> <button class="btn-listen-inline" onclick="playLessonTTS('${ttsText.replace(/'/g, "&#39;")}')">🔊 Listen</button></li>`;
                } else if (typeof ex === 'object') {
                    const french = ex.french || ex.text || ex.example || '';
                    const english = ex.english || ex.translation || '';
                    const ttsText = french.replace(/\([^)]*\)/g, '').replace(/\*\*/g, '').trim();
                    if (french) {
                        html += `<li><strong>${french}</strong>${english ? ` <span class="muted">(${english})</span>` : ''} <button class="btn-listen-inline" onclick="playLessonTTS('${ttsText.replace(/'/g, "&#39;")}')">🔊 Listen</button></li>`;
                    }
                }
            });
            html += '</ul></div>';
            hasContent = true;
        }
    }
    
    if (!hasContent) {
        html += '<div style="background: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; color: #666;">';
        html += '<p>📖 Grammar explanation will be generated</p>';
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

function createInteractiveVocabulary(vocabContent) {
    // Handle different vocabulary formats
    let vocabItems = [];
    
    if (Array.isArray(vocabContent)) {
        // Already an array
        vocabItems = vocabContent.map(item => {
            if (typeof item === 'string') {
                return { front: item, back: '', pronunciation: '' };
            } else if (typeof item === 'object' && item.word) {
                // Handle curriculum parser format: word, english, example
                return {
                    front: item.word,
                    back: item.english || item.definition || item.context_example || '',
                    pronunciation: item.pronunciation_tip || item.pronunciation || ''
                };
            } else if (typeof item === 'object' && item.front) {
                return item;
            } else if (typeof item === 'object') {
                // Try to find a property that might be the word/text
                const text = item.word || item.front || item.french || item.text || item.phrase || item.example || Object.values(item).find(v => typeof v === 'string') || '';
                const back = item.definition || item.english || item.translation || item.example || '';
                return { front: text || back, back: back, pronunciation: item.pronunciation_tip || item.pronunciation || '' };
            }
            return { front: String(item), back: '', pronunciation: '' };
        });
    } else if (typeof vocabContent === 'object' && vocabContent.words) {
        // Object with words property
        vocabItems = vocabContent.words.map(item => ({
            front: item.word || item.text || item.phrase || item.french || item.front || item.definition || '',
            back: item.definition || item.context_example || item.english || item.translation || '',
            pronunciation: item.pronunciation_tip || item.pronunciation || ''
        }));
    } else if (typeof vocabContent === 'string') {
        // Single string
        vocabItems = [{ front: vocabContent, back: '', pronunciation: '' }];
    }
    
    // Ensure front text exists for each item
    vocabItems = vocabItems.map(item => {
        if (!item) {
            return item;
        }
        const front = item.front && item.front.trim().length > 0 ? item.front : (item.back || '');
        return { ...item, front };
    }).filter(item => item && item.front && item.front.trim().length > 0);
    
    if (!vocabItems || vocabItems.length === 0) {
        return '<p>No vocabulary content available.</p>';
    }
    
    let html = '<div class="lesson-section-interactive vocab-drill">';
    html += '<h3>🔤 Vocabulary Drill</h3>';
    html += '<p>Learn these key words and phrases:</p>';
    html += '<div class="vocab-flashcards">';
    
    vocabItems.forEach((item) => {
        const frontText = item.front || '';
        const backText = item.back || '';
        const pronunciation = item.pronunciation || '';
        // Handle gender notation like "étudiant(e)" - remove the parentheses for TTS
        // Also remove bold markdown markers
        const ttsText = frontText.replace(/\([^)]*\)/g, '').replace(/\*\*/g, '').trim();
        
        // Always create Listen button if we have text
        if (frontText.trim()) {
            html += `
            <div class="vocab-card-mini" onclick="this.classList.toggle('flipped')">
                <div class="card-inner">
                    <div class="card-front">
                        ${frontText}
                        <button class="vocab-tts-mini" onclick="event.stopPropagation(); playLessonTTS('${ttsText.replace(/'/g, "&#39;")}')">Listen</button>
                    </div>
                    <div class="card-back">
                        <div class="vocab-back-text">${backText || frontText}</div>
                        ${pronunciation ? `<div class="vocab-pronunciation">${pronunciation}</div>` : ''}
                    </div>
                </div>
            </div>
            `;
        }
    });
    
    html += '</div>';
    html += '<p style="text-align: center; margin-top: 20px; font-size: 0.9em;">Click cards to flip</p>';
    html += '</div>';
    return html;
}

function createInteractiveSpeaking(speakingContent) {
    if (!speakingContent) {
        return '<p>No speaking practice available.</p>';
    }
    
    let html = '<div class="lesson-section-interactive speaking-drill">';
    html += '<h3>🎤 Speaking Practice</h3>';
    
    let prompt = '';
    let targets = [];
    
    if (typeof speakingContent === 'string') {
        prompt = speakingContent;
    } else if (typeof speakingContent === 'object') {
        if (speakingContent.prompt) {
            prompt = speakingContent.prompt;
        }
        if (speakingContent.targets && Array.isArray(speakingContent.targets)) {
            targets = speakingContent.targets;
        } else if (speakingContent.success_criteria) {
            targets = [speakingContent.success_criteria];
        }
    }
    
    if (prompt) {
        html += `<p><strong>Scenario:</strong> ${prompt}</p>`;
    }
    
    if (targets && targets.length > 0) {
        html += '<p><strong>Try to say:</strong></p><ul>';
        targets.forEach(target => {
            html += `<li>${target}</li>`;
        });
        html += '</ul>';
    }
    
    html += `
    <div class="speaking-practice-embedded">
        <div class="speaking-controls">
            <button class="btn-primary btn-large embedded-ptt-btn" type="button">Hold to Speak</button>
            <span class="embedded-recording-status" style="display: none;"></span>
        </div>
        <div class="embedded-feedback-box" style="display: none;">
            <p class="embedded-feedback-label"><strong>Feedback</strong></p>
            <div class="embedded-feedback-content"></div>
            <button class="btn-secondary embedded-play-feedback" type="button" style="display: none;">🔊 Play Feedback</button>
        </div>
    </div>
    `;
    html += '</div>';
    return html;
}

function setupEmbeddedSpeaking(container, speakingContent) {
    const speakingRoot = container.querySelector('.speaking-practice-embedded');
    if (!speakingRoot) {
        return;
    }

    const pttBtn = speakingRoot.querySelector('.embedded-ptt-btn');
    const statusEl = speakingRoot.querySelector('.embedded-recording-status');
    const feedbackBox = speakingRoot.querySelector('.embedded-feedback-box');
    const feedbackContent = speakingRoot.querySelector('.embedded-feedback-content');
    const playBtn = speakingRoot.querySelector('.embedded-play-feedback');

    const scenario = speakingContent?.scenario_prompt
        || speakingContent?.prompt
        || speakingContent?.scenario_context
        || speakingContent?.scenario_domain
        || 'Speaking practice';

    const targets = Array.isArray(speakingContent?.targets) && speakingContent.targets.length > 0
        ? speakingContent.targets
        : (Array.isArray(speakingContent?.target_phrases) ? speakingContent.target_phrases : []);

    let mediaRecorder = null;
    let audioChunks = [];
    let audioStream = null;
    let isRecording = false;
    let lastFeedback = '';

    const startRecording = async () => {
        if (isRecording) {
            return;
        }
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                await processAudio(audioBlob);
                audioStream?.getTracks().forEach(track => track.stop());
                audioStream = null;
            };

            mediaRecorder.start();
            isRecording = true;
            pttBtn.classList.add('active');
            statusEl.textContent = '🎤 Recording...';
            statusEl.style.display = 'inline-block';
        } catch (error) {
            statusEl.textContent = '❌ Microphone access denied';
            statusEl.style.display = 'inline-block';
            console.error('Embedded speaking error:', error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            pttBtn.classList.remove('active');
            statusEl.textContent = '⏳ Processing...';
        }
    };

    const processAudio = async (audioBlob) => {
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');
            formData.append('targets', JSON.stringify(targets));  // Send hints for better accuracy

            const transcribeResponse = await fetch(`${API_BASE}/api/audio/transcribe`, {
                method: 'POST',
                body: formData
            });
            const { text: transcription } = await transcribeResponse.json();

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

            lastFeedback = feedback || '';
            feedbackContent.textContent = lastFeedback || 'No feedback returned.';
            feedbackBox.style.display = 'block';
            playBtn.style.display = lastFeedback ? 'inline-block' : 'none';
            statusEl.textContent = '✅ Done!';
        } catch (error) {
            statusEl.textContent = '❌ Error processing audio';
            console.error('Embedded speaking processing error:', error);
        }
    };

    const playFeedback = async () => {
        if (!lastFeedback) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE}/api/audio/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: lastFeedback, lang: 'fr' })
            });
            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            const audio = new Audio(audioUrl);
            audio.play();
        } catch (error) {
            console.error('Embedded speaking TTS error:', error);
        }
    };

    pttBtn.addEventListener('mousedown', startRecording);
    pttBtn.addEventListener('mouseup', stopRecording);
    pttBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    pttBtn.addEventListener('touchend', (e) => {
        e.preventDefault();
        stopRecording();
    });
    playBtn.addEventListener('click', playFeedback);
}

function createInteractiveQuiz(quizContent) {
    if (!quizContent) {
        return '<p>No quiz available.</p>';
    }
    
    // Handle different quiz formats
    let questions = [];
    if (Array.isArray(quizContent)) {
        // Simple array of question strings
        questions = quizContent.map((q, idx) => ({
            id: idx,
            question: typeof q === 'string' ? q : (q.question || q.question_text || ''),
            options: q.options || []
        }));
    } else if (quizContent.questions && Array.isArray(quizContent.questions)) {
        // Structured quiz with questions array
        questions = quizContent.questions;
    }

    questions = normalizeQuizQuestions(questions);
    
    if (questions.length === 0) {
        return '<p>No quiz questions available.</p>';
    }
    
    let html = '<div class="lesson-section-interactive quiz-section">';
    html += `<h3>❓ Quiz (${questions.length} questions)</h3>`;
    html += '<div class="quiz-interactive">';
    
    questions.forEach((question, idx) => {
        const questionId = `quiz-q${idx}`;
        const questionText = typeof question === 'string' ? question : (question.question || question.question_text || '');
        const options = question.options || [];
        const questionTts = getQuizAudioText(questionText, question).replace(/\([^)]*\)/g, '').replace(/\*\*/g, '').trim();
        const listenButton = questionTts
            ? ` <button class="btn-listen-inline" onclick="playLessonTTS('${questionTts.replace(/'/g, "&#39;")}')">🔊 Listen</button>`
            : '';
        
        html += `
        <div class="quiz-question-interactive" data-question="${idx}">
            <h4>${idx + 1}. ${questionText}${listenButton}</h4>
        `;
        
        if (options && Array.isArray(options) && options.length > 0) {
            html += '<div class="quiz-options-interactive">';
            options.forEach((option, optIdx) => {
                const optionId = `${questionId}-opt${optIdx}`;
                const optionTts = String(option).replace(/\([^)]*\)/g, '').replace(/\*\*/g, '').trim();
                const optionListen = optionTts
                    ? `<button class="btn-listen-inline" onclick="event.preventDefault(); event.stopPropagation(); playLessonTTS('${optionTts.replace(/'/g, "&#39;")}')">🔊</button>`
                    : '';
                html += `
                <label class="quiz-option-label">
                    <input type="radio" name="${questionId}" value="${optIdx}" class="quiz-option-input">
                    <span class="quiz-option-text">${option}</span>
                    ${optionListen}
                </label>
                `;
            });
            html += '</div>';
        } else {
            // Text input for questions without options
            html += `<div class="quiz-input-wrapper"><input type="text" name="${questionId}" class="quiz-input" placeholder="Your answer..."></div>`;
        }
        
        html += '</div>';
    });
    
    html += '</div>';
    html += `
    <div class="quiz-action">
        <button class="btn-primary btn-large" onclick="submitQuiz()">
            Submit Quiz
        </button>
    </div>
    `;
    html += '</div>';
    return html;
}

function startSpeakingPractice(button) {
    // Simple placeholder - just mark as done for now
    const transcriptDiv = button.parentElement.querySelector('#speaking-transcript');
    transcriptDiv.style.display = 'block';
    button.style.display = 'none';
}

function submitQuiz() {
    const quizDiv = document.querySelector('.quiz-interactive');
    if (!quizDiv) {
        alert('Quiz not found');
        return;
    }
    
    const lesson = window.currentLessonModal.lesson;
    if (!lesson || !lesson.content || !lesson.content.quiz) {
        alert('Quiz data not found');
        return;
    }
    
    const questions = lesson.content.quiz;
    
    // Handle both formats
    let questionArray = [];
    if (Array.isArray(questions)) {
        questionArray = questions;
    } else if (questions.questions && Array.isArray(questions.questions)) {
        questionArray = questions.questions;
    }

    questionArray = normalizeQuizQuestions(questionArray);
    
    if (questionArray.length === 0) {
        alert('No questions to grade');
        return;
    }
    
    // Collect all student answers first
    const studentAnswers = {};
    const questionDivs = document.querySelectorAll('.quiz-question-interactive');
    
    questionDivs.forEach((qDiv, idx) => {
        const questionId = `quiz-q${idx}`;
        const radioInputs = qDiv.querySelectorAll(`input[name="${questionId}"][type="radio"]:checked`);
        const textInput = qDiv.querySelector(`input[name="${questionId}"][type="text"]`);
        
        if (radioInputs.length > 0) {
            // Multiple choice - get the selected option index
            studentAnswers[idx] = radioInputs[0].value;
        } else if (textInput && textInput.value.trim()) {
            // Text answer
            studentAnswers[idx] = textInput.value.trim();
        }
    });
    
    // Check if all questions answered
    if (Object.keys(studentAnswers).length < questionArray.length) {
        alert('Please answer all questions before submitting.');
        return;
    }
    
    let score = 0;
    const results = [];
    
    // Grade each question
    questionArray.forEach((question, idx) => {
        const studentAnswer = studentAnswers[idx];
        let isCorrect = false;
        let correctAnswer = '';
        
        if (!studentAnswer) {
            results.push({
                index: idx,
                question: question.question || question,
                studentAnswer: 'No answer provided',
                correctAnswer: question.correct_answer || 'Unknown',
                isCorrect: false
            });
            return;
        }
        
        // Get the correct answer
        if (question.correct_answer !== undefined && question.correct_answer !== null) {
            correctAnswer = String(question.correct_answer).trim();
            
            // Handle multiple choice (studentAnswer is an index, correct_answer could be index or value)
            if (question.options && Array.isArray(question.options)) {
                let correctIdx = -1;
                const numericAnswer = Number.parseInt(correctAnswer, 10);
                if (!Number.isNaN(numericAnswer) && numericAnswer >= 0 && numericAnswer < question.options.length) {
                    correctIdx = numericAnswer;
                    correctAnswer = String(question.options[correctIdx]);
                } else {
                    correctIdx = question.options.findIndex(opt => 
                        normalizeQuizText(opt) === normalizeQuizText(correctAnswer)
                    );
                }

                if (correctIdx >= 0 && question.options[correctIdx] !== undefined) {
                    correctAnswer = String(question.options[correctIdx]);
                }
                
                const studentIdx = Number.parseInt(studentAnswer, 10);
                const studentOption = (!Number.isNaN(studentIdx) && question.options[studentIdx] !== undefined)
                    ? String(question.options[studentIdx])
                    : '';

                if (studentIdx === correctIdx || (studentOption && normalizeQuizText(studentOption) === normalizeQuizText(correctAnswer))) {
                    score++;
                    isCorrect = true;
                }
                
                // Highlight answers in UI
                document.querySelectorAll(`[name="quiz-q${idx}"]`).forEach((input, optIdx) => {
                    const label = input.parentElement;
                    if (optIdx === correctIdx) {
                        label.style.backgroundColor = '#d4edda';
                        label.style.borderColor = '#28a745';
                    } else if (input.checked && optIdx !== correctIdx) {
                        label.style.backgroundColor = '#f8d7da';
                        label.style.borderColor = '#dc3545';
                    }
                });
            } else {
                // Free text answer - flexible matching
                const studentNorm = normalizeQuizText(studentAnswer);
                const correctNorm = normalizeQuizText(correctAnswer);
                
                if (studentNorm === correctNorm) {
                    score++;
                    isCorrect = true;
                }
                
                const input = document.querySelector(`[name="quiz-q${idx}"][type="text"]`);
                if (input) {
                    input.style.backgroundColor = isCorrect ? '#d4edda' : '#f8d7da';
                    input.style.borderColor = isCorrect ? '#28a745' : '#dc3545';
                }
            }
        } else {
            // No correct_answer provided in question
            correctAnswer = 'Not specified';
        }
        
        const displayCorrectAnswer = correctAnswer && correctAnswer.trim().length > 0
            ? correctAnswer
            : 'Not specified';

        results.push({
            index: idx,
            question: question.question || String(question),
            studentAnswer: studentAnswer,
            correctAnswer: displayCorrectAnswer,
            isCorrect: isCorrect
        });
    });
    
    const percentage = Math.round((score / questionArray.length) * 100);
    
    // Build detailed results HTML
    let resultsHTML = '<div class="quiz-results-details" style="margin-top: 20px; text-align: left;">';
    resultsHTML += '<h4 style="margin-bottom: 15px;">Review Your Answers:</h4>';
    results.forEach((result) => {
        const icon = result.isCorrect ? '✅' : '❌';
        const bgColor = result.isCorrect ? '#d4edda' : '#f8d7da';
        const borderColor = result.isCorrect ? '#28a745' : '#dc3545';
        resultsHTML += `
            <div style="background: ${bgColor}; border: 1px solid ${borderColor}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <p style="margin: 5px 0;"><strong>${icon} Question ${result.index + 1}:</strong> ${result.question}</p>
                <p style="margin: 5px 0;"><strong>Your Answer:</strong> ${result.studentAnswer}</p>
                ${!result.isCorrect ? `<p style="margin: 5px 0; color: #28a745;"><strong>✓ Correct Answer:</strong> ${result.correctAnswer || 'Not specified'}</p>` : ''}
            </div>
        `;
    });
    resultsHTML += '</div>';
    
    // Show results
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'quiz-results';
    resultsDiv.innerHTML = `
        <div class="results-score">
            <h3>Your Score: ${score}/${questionArray.length} (${percentage}%)</h3>
            <p>${percentage >= 70 ? '✅ Great job!' : '⚠️ Keep practicing!'}</p>
        </div>
        ${resultsHTML}
    `;
    
    quizDiv.appendChild(resultsDiv);
    document.querySelector('.quiz-action').style.display = 'none';
}

/**
 * UI Enhancement Module for French Tutor
 * Handles:
 * - Standardized 3-button navigation
 * - Vocabulary French-side listening
 * - Listen icons on examples
 * - Quiz answer validation feedback
 * - Progress tracking display
 */

const UIEnhancements = {
    /**
     * Standardized lesson navigation buttons
     * Replaces all lesson navigation with consistent Back/Next/Exit pattern
     */
    createLessonNavigation(onBack, onNext, onExit, isLastStep = false) {
        const nav = document.createElement('div');
        nav.className = 'lesson-navigation';
        nav.innerHTML = `
            <button class="btn-nav btn-back" title="Go to previous step">← Back</button>
            <button class="btn-nav btn-${isLastStep ? 'complete' : 'next'}" title="${isLastStep ? 'Complete lesson' : 'Go to next step'}">
                ${isLastStep ? 'Next Lesson' : 'Next'} →
            </button>
            <button class="btn-nav btn-exit" title="Return to lesson selection">Exit Lesson</button>
        `;
        
        nav.querySelector('.btn-back').addEventListener('click', onBack);
        nav.querySelector(`.btn-${isLastStep ? 'complete' : 'next'}`).addEventListener('click', onNext);
        nav.querySelector('.btn-exit').addEventListener('click', onExit);
        
        return nav;
    },
    
    /**
     * Enhanced vocabulary card with French-side listening
     * Plays word pronunciation from French side
     */
    createVocabCard(word, translation, examples = [], isFrench = true) {
        const card = document.createElement('div');
        card.className = 'vocab-card';
        
        // Determine which side is flipped
        const [frontText, backText] = isFrench 
            ? [word, translation]
            : [translation, word];
        
        card.innerHTML = `
            <div class="vocab-card-inner" data-flipped="false">
                <div class="vocab-card-front">
                    <div class="vocab-text">${frontText}</div>
                    ${isFrench ? `
                        <button class="btn-listen" title="Listen to pronunciation" data-word="${word}">
                            🔊 Listen
                        </button>
                    ` : ''}
                </div>
                <div class="vocab-card-back">
                    <div class="vocab-text">${backText}</div>
                </div>
            </div>
            ${examples.length > 0 ? `
                <div class="vocab-examples">
                    <p><strong>Examples:</strong></p>
                    <ul>
                        ${examples.map(ex => `
                            <li>
                                <span class="example-fr">${ex}</span>
                                <button class="btn-listen-example" data-text="${ex}" title="Listen to example">
                                    🔊
                                </button>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        // Card flip handler
        card.querySelector('.vocab-card-inner').addEventListener('click', function() {
            const isFlipped = this.dataset.flipped === 'true';
            this.dataset.flipped = !isFlipped;
            
            // If flipping to show French (from English), play pronunciation
            if (!isFlipped && isFrench) {
                setTimeout(() => {
                    UIEnhancements.playAudio(word, 'fr');
                }, 300);
            }
        });
        
        // Listen button handlers
        card.querySelector('.btn-listen')?.addEventListener('click', (e) => {
            e.stopPropagation();
            UIEnhancements.playAudio(word, 'fr');
        });
        
        card.querySelectorAll('.btn-listen-example').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const text = btn.dataset.text;
                UIEnhancements.playAudio(text, 'fr');
            });
        });
        
        return card;
    },
    
    /**
     * Play audio for text (French)
     */
    playAudio(text, lang = 'fr') {
        fetch(`${API_BASE}/api/audio/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, lang })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.play();
        })
        .catch(err => console.error('Audio playback failed:', err));
    },
    
    /**
     * Quiz question with hidden answers
     * Shows answers only after submission
     */
    createQuizQuestion(question, questionId, showAnswerKey = false) {
        const container = document.createElement('div');
        container.className = 'quiz-question';
        container.dataset.questionId = questionId;
        
        let html = `
            <div class="question-text">
                <strong>${question.question_text}</strong>
            </div>
        `;
        
        if (question.question_type === 'mcq') {
            html += `
                <div class="question-options">
                    ${question.options.map((opt, idx) => `
                        <label class="option-label">
                            <input type="radio" name="q-${questionId}" value="${opt}" data-index="${idx}">
                            <span>${showAnswerKey && opt === question.correct_answer ? '✓ ' : ''}${opt}</span>
                        </label>
                    `).join('')}
                </div>
            `;
        } else {
            html += `
                <input type="text" class="answer-input" placeholder="Your answer..." 
                       data-question-id="${questionId}">
            `;
        }
        
        if (showAnswerKey && question.correct_answer) {
            html += `
                <div class="answer-key" style="margin-top: 15px; padding: 10px; background: #f0f0f0; border-left: 4px solid #4CAF50;">
                    <strong>Correct answer:</strong> ${question.correct_answer}
                </div>
            `;
        }
        
        container.innerHTML = html;
        return container;
    },
    
    /**
     * Quiz result feedback with answer comparison
     */
    createQuizFeedback(question, studentAnswer, isCorrect, validationResult = null) {
        const feedback = document.createElement('div');
        feedback.className = `quiz-feedback ${isCorrect ? 'correct' : 'incorrect'}`;
        
        let message = isCorrect ? '✓ Correct!' : '✗ Incorrect';
        
        if (validationResult) {
            if (validationResult.is_correct) {
                message = '✓ Perfect!';
            } else if (validationResult.is_close) {
                message = `⚠ ${validationResult.feedback}`;
                feedback.classList.add('warning');
            } else {
                message = `✗ ${validationResult.feedback}`;
            }
        }
        
        feedback.innerHTML = `
            <div class="feedback-message">${message}</div>
            ${validationResult && validationResult.warnings.length > 0 ? `
                <div class="feedback-warnings">
                    ${validationResult.warnings.map(w => `<small>• ${w.replace(/_/g, ' ')}</small>`).join('<br>')}
                </div>
            ` : ''}
        `;
        
        return feedback;
    },
    
    /**
     * Lesson status indicators for lesson selection
     */
    createLessonStatusIndicator(lesson) {
        const status = lesson.status || 'not_started';
        const themes = {
            'completed': { color: '#4CAF50', label: '✓ Completed' },
            'in_progress': { color: '#FFC107', label: '● In Progress' },
            'not_started': { color: '#BDBDBD', label: '○ Not Started' }
        };
        
        const theme = themes[status];
        const indicator = document.createElement('span');
        indicator.className = `lesson-status-${status}`;
        indicator.style.display = 'inline-block';
        indicator.style.padding = '5px 10px';
        indicator.style.backgroundColor = theme.color;
        indicator.style.color = 'white';
        indicator.style.borderRadius = '4px';
        indicator.style.fontSize = '12px';
        indicator.style.marginLeft = '10px';
        indicator.textContent = theme.label;
        
        return indicator;
    },
    
    /**
     * Modal for in-lesson components (speaking practice, etc)
     */
    createLessonModal(title, content, buttons = []) {
        const modal = document.createElement('div');
        modal.className = 'lesson-modal';
        
        modal.innerHTML = `
            <div class="lesson-modal-overlay"></div>
            <div class="lesson-modal-content">
                <div class="lesson-modal-header">
                    <h3>${title}</h3>
                    <button class="btn-close-modal" aria-label="Close">×</button>
                </div>
                <div class="lesson-modal-body">
                    ${typeof content === 'string' ? content : ''}
                </div>
                <div class="lesson-modal-footer">
                    ${buttons.map(btn => `
                        <button class="btn-secondary" data-action="${btn.action}">
                            ${btn.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        if (typeof content !== 'string' && content instanceof HTMLElement) {
            modal.querySelector('.lesson-modal-body').appendChild(content);
        }
        
        modal.querySelector('.btn-close-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.querySelector('.lesson-modal-overlay').addEventListener('click', () => {
            modal.remove();
        });
        
        return modal;
    },
    
    /**
     * Post-lesson completion options
     */
    createPostLessonOptions(onReview, onNext, onDashboard) {
        const container = document.createElement('div');
        container.className = 'post-lesson-options';
        
        container.innerHTML = `
            <div class="post-lesson-message">
                <h2>✓ Lesson Complete!</h2>
                <p>Good job! What would you like to do next?</p>
            </div>
            <div class="post-lesson-buttons">
                <button class="btn-secondary btn-review">← Review Lesson</button>
                <button class="btn-primary btn-next">Next Lesson →</button>
                <button class="btn-secondary btn-dashboard">📊 Dashboard</button>
            </div>
        `;
        
        container.querySelector('.btn-review').addEventListener('click', onReview);
        container.querySelector('.btn-next').addEventListener('click', onNext);
        container.querySelector('.btn-dashboard').addEventListener('click', onDashboard);
        
        return container;
    }
};

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIEnhancements;
}

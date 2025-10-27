/**
 * Chat Component
 * ==============
 * Handles chat interface and messaging
 */

import apiService from '../services/api.js';
import { showNotification } from '../utils/notifications.js';

class ChatComponent {
    constructor() {
        this.messageInput = null;
        this.sendButton = null;
        this.messagesList = null;
        this.currentModel = 'llama-3.1-8b-instant';
        this.isTyping = false;
        
        this.init();
    }

    init() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendBtn');
        this.messagesList = document.getElementById('messagesList');
        
        this.setupEventListeners();
        this.setupSendButton();
    }

    setupEventListeners() {
        if (this.messageInput) {
            this.messageInput.addEventListener('input', (e) => this.handleInputChange(e));
            this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        }

        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
    }

    setupSendButton() {
        if (!this.sendButton || !this.messageInput) return;

        // Visual feedback for typing
        this.messageInput.addEventListener('input', (e) => {
            const hasContent = e.target.value.trim().length > 0;
            
            if (hasContent) {
                this.sendButton.classList.add('typing');
                this.sendButton.disabled = false;
                this.messageInput.classList.add('typing');
            } else {
                this.sendButton.classList.remove('typing');
                this.sendButton.disabled = true;
                this.messageInput.classList.remove('typing');
            }
        });
    }

    handleInputChange(e) {
        const input = e.target;
        const sendBtn = this.sendButton;
        
        if (sendBtn) {
            sendBtn.disabled = !input.value.trim();
        }

        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    async sendMessage() {
        const message = this.messageInput?.value.trim();
        
        if (!message || this.isTyping) return;

        try {
            // Clear input and show loading
            this.messageInput.value = '';
            this.messageInput.style.height = 'auto';
            this.sendButton.disabled = true;
            this.isTyping = true;

            // Show chat screen if on welcome screen
            this.showChatScreen();

            // Add user message
            this.addMessage(message, 'user');

            // Show typing indicator
            this.showTypingIndicator();

            // Send to API
            const response = await apiService.sendMessage(message, this.currentModel);
            
            // Hide typing indicator and show response
            this.hideTypingIndicator();
            this.addMessage(response.response, 'assistant', response);

            showNotification('Message sent successfully', 'success');

        } catch (error) {
            console.error('Send message error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            showNotification('Failed to send message', 'error');
        } finally {
            this.isTyping = false;
        }
    }

    addMessage(content, sender, metadata = {}) {
        if (!this.messagesList) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-brain"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        
        if (sender === 'assistant' && metadata.model_used) {
            const modelInfo = `${metadata.model_used} • ${metadata.response_time?.toFixed(2)}s`;
            meta.innerHTML = `<span>${modelInfo}</span><span>${new Date().toLocaleTimeString()}</span>`;
        } else {
            meta.innerHTML = `<span>${new Date().toLocaleTimeString()}</span>`;
        }
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(meta);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesList.appendChild(messageDiv);
        messageDiv.classList.add('fade-in');
        
        // Scroll to bottom
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }

    showTypingIndicator() {
        if (!this.messagesList) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-brain"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        this.messagesList.appendChild(typingDiv);
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator?.remove();
    }

    showChatScreen() {
        const welcomeScreen = document.getElementById('welcomeScreen');
        const messagesContainer = document.getElementById('messagesContainer');
        
        if (welcomeScreen && messagesContainer) {
            welcomeScreen.style.display = 'none';
            messagesContainer.style.display = 'flex';
        }
    }

    setCurrentModel(model) {
        this.currentModel = model;
    }
}

export default ChatComponent;
/**
 * Chat Module
 * ===========
 * Handles chat functionality including message sending, display, and AI interaction
 */

class ChatModule {
    constructor(app) {
        this.app = app;
        this.isTyping = false;
        this.lastResponseInfo = null;
        
        this.init();
    }

    init() {
        this.setupChatEventListeners();
        this.setupAutoResize();
    }

    setupChatEventListeners() {
        // Input controls
        const messageInput = document.getElementById("messageInput");
        const sendBtn = document.getElementById("sendBtn");

        messageInput?.addEventListener("input", (e) => this.handleInputChange(e));
        messageInput?.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn?.addEventListener("click", () => this.sendMessage());

        // Quick actions
        document.querySelectorAll(".quick-action").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    setupAutoResize() {
        const textarea = document.getElementById("messageInput");
        if (!textarea) return;

        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    }

    showWelcomeScreen() {
        const welcomeScreen = document.getElementById("welcomeScreen");
        const messagesContainer = document.getElementById("messagesContainer");

        if (welcomeScreen && messagesContainer) {
            welcomeScreen.style.display = "flex";
            messagesContainer.style.display = "none";
        }
    }

    showChatScreen() {
        const welcomeScreen = document.getElementById("welcomeScreen");
        const messagesContainer = document.getElementById("messagesContainer");

        if (welcomeScreen && messagesContainer) {
            welcomeScreen.style.display = "none";
            messagesContainer.style.display = "flex";
        }
    }

    handleInputChange(e) {
        const input = e.target;
        const sendBtn = document.getElementById("sendBtn");

        if (sendBtn) {
            sendBtn.disabled = !input.value.trim();
        }

        // Auto-resize
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 120) + "px";
    }

    async sendMessage() {
        const messageInput = document.getElementById("messageInput");
        const message = messageInput?.value.trim();

        if (!message || this.isTyping) return;

        // Clear input and disable send button
        messageInput.value = "";
        messageInput.style.height = "auto";
        const sendBtn = document.getElementById("sendBtn");
        if (sendBtn) sendBtn.disabled = true;

        this.isTyping = true;
        this.showChatScreen();
        this.addMessage(message, "user");
        this.showTypingIndicator();

        try {
            // Send to AI
            const response = await this.callAI(message);
            this.hideTypingIndicator();
            this.addMessage(response, "assistant");
        } catch (error) {
            console.error("Error sending message:", error);
            this.hideTypingIndicator();
            this.addMessage("Sorry, I encountered an error. Please try again.", "assistant");
        } finally {
            this.isTyping = false;
        }
    }

    addMessage(content, sender) {
        const messagesList = document.getElementById("messagesList");
        if (!messagesList) return;

        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.innerHTML = sender === "user" 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-brain"></i>';

        const messageContent = document.createElement("div");
        messageContent.className = "message-content";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";

        const text = document.createElement("div");
        text.className = "message-text";
        text.innerHTML = this.formatMessage(content, sender);

        const meta = document.createElement("div");
        meta.className = "message-meta";

        // Add model info for assistant messages
        if (sender === "assistant") {
            const responseInfo = this.lastResponseInfo || {};
            const modelName = this.app.formatModelName(
                responseInfo.model_used || this.app.currentModel
            );
            const providerName = responseInfo.provider_used || "groq";
            const responseTime = responseInfo.response_time || 0;

            const providerBadge = `<span class="provider-badge provider-${providerName}">${this.app.getProviderDisplayName(providerName)}</span>`;
            const timingInfo = responseTime > 0 
                ? `<span class="timing-info">${responseTime.toFixed(2)}s</span>` 
                : "";

            meta.innerHTML = `
                <div class="model-info">
                    <span class="model-name">${modelName}</span>
                    ${providerBadge}
                    ${timingInfo}
                </div>
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            `;
        } else {
            meta.innerHTML = `<span class="timestamp">${new Date().toLocaleTimeString()}</span>`;
        }

        bubble.appendChild(text);
        messageContent.appendChild(bubble);
        messageContent.appendChild(meta);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        messagesList.appendChild(messageDiv);
        messageDiv.classList.add("fade-in");

        // Scroll to bottom
        messagesList.scrollTop = messagesList.scrollHeight;

        // Save to current conversation
        if (this.app.currentConversation) {
            this.app.currentConversation.messages.push({
                content: content,
                sender: sender,
                timestamp: new Date(),
                model: sender === "assistant" ? this.app.currentModel : null
            });
            this.app.saveConversations();
        }
    }

    showTypingIndicator() {
        const messagesList = document.getElementById("messagesList");
        if (!messagesList) return;

        const typingDiv = document.createElement("div");
        typingDiv.className = "message assistant typing-indicator";
        typingDiv.id = "typingIndicator";

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

        messagesList.appendChild(typingDiv);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById("typingIndicator");
        typingIndicator?.remove();
    }

    async callAI(message) {
        // Get selected model
        const selectedModel = this.app.currentModel || "llama-3.1-8b-instant";

        try {
            const apiResponse = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: message,
                    model: selectedModel,
                    auto_select: false,
                    guardrails_enabled: this.app.getActiveGuardrails(),
                }),
            });

            if (!apiResponse.ok) {
                throw new Error(`HTTP error! status: ${apiResponse.status}`);
            }

            const data = await apiResponse.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Store provider and model information for display
            this.lastResponseInfo = {
                model_used: data.model_used || selectedModel,
                provider_used: data.provider_used || "groq",
                response_time: data.response_time || 0,
            };

            let responseText = data.response || data.message || "No response received";

            // Handle guardrails blocking
            if (data.blocked) {
                responseText = `⚠️ ${responseText}`;
            }

            return responseText;
        } catch (error) {
            console.error("AI API Error:", error);
            throw new Error(`Failed to get AI response: ${error.message}`);
        }
    }

    formatMessage(content, sender) {
        if (sender === "user") {
            return content.replace(/\n/g, "<br>");
        }

        // Format assistant messages with better styling
        let formatted = content;

        // Convert markdown-style formatting
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");
        formatted = formatted.replace(/`(.*?)`/g, "<code>$1</code>");
        formatted = formatted.replace(/\n/g, "<br>");

        // Format code blocks
        formatted = formatted.replace(
            /```([\s\S]*?)```/g,
            '<pre><code>$1</code></pre>'
        );

        return formatted;
    }

    handleQuickAction(action) {
        const messageInput = document.getElementById("messageInput");
        if (!messageInput) return;

        const prompts = {
            code: "Help me write code for: ",
            write: "Help me write: ",
            analyze: "Please analyze: ",
            creative: "Create something creative about: "
        };

        const prompt = prompts[action] || "";
        messageInput.value = prompt;
        messageInput.focus();
        
        // Position cursor at the end
        messageInput.setSelectionRange(prompt.length, prompt.length);
        
        // Trigger input event to enable send button
        messageInput.dispatchEvent(new Event('input'));
    }

    // Public methods for external access
    clearChat() {
        const messagesList = document.getElementById("messagesList");
        if (messagesList) {
            messagesList.innerHTML = "";
        }
        this.showWelcomeScreen();
    }

    getCurrentMessages() {
        return this.app.currentConversation?.messages || [];
    }
}

export default ChatModule;
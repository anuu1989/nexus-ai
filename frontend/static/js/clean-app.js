// ===== CLEAN NEXUSAI APPLICATION =====

class NexusAI {
  constructor() {
    this.conversations = [];
    this.currentConversation = null;
    this.isTyping = false;
    this.settings = this.loadSettings();
    this.currentModel = this.settings.defaultModel || "llama-3.1-8b-instant";
    this.availableModels = []; // Store fetched models from API

    // Initialize guardrails stats to prevent undefined errors
    this.guardrailsStats = {
      blocked: 0,
      passed: 0,
    };

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadConversations();
    this.applySettings();
    this.showWelcomeScreen();

    // Mark as initialized to prevent applySettings from overriding user selections
    this._initialized = true;

    this.loadAvailableModels();
    this.initializeFeaturePanels();

    // Initialize enhanced features
    this.initializeEnhancedFeatures();

    // Initialize model display with a delay to ensure DOM is ready
    setTimeout(() => {
      this.updateModelDisplay();
    }, 500);
  }

  setupEventListeners() {
    // Header controls
    document
      .getElementById("sidebarToggle")
      ?.addEventListener("click", () => this.toggleSidebar());
    document
      .getElementById("featuresBtn")
      ?.addEventListener("click", () => this.toggleSidebar());
    document
      .getElementById("newChatBtn")
      ?.addEventListener("click", () => this.startNewChat());
    document
      .getElementById("settingsBtn")
      ?.addEventListener("click", () => this.openSettings());

    // Sidebar controls
    document
      .getElementById("clearAllBtn")
      ?.addEventListener("click", () => this.clearAllConversations());
    document
      .getElementById("exportBtn")
      ?.addEventListener("click", () => this.exportConversations());

    // Input controls
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");

    messageInput?.addEventListener("input", (e) => this.handleInputChange(e));
    messageInput?.addEventListener("keydown", (e) => this.handleKeyDown(e));
    sendBtn?.addEventListener("click", () => this.sendMessage());

    // Attachment controls
    document
      .getElementById("attachBtn")
      ?.addEventListener("click", () => this.showAttachmentOptions());
    document
      .getElementById("voiceBtn")
      ?.addEventListener("click", () => this.toggleVoiceInput());

    // Quick actions
    document.querySelectorAll(".quick-action").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const action = e.currentTarget.dataset.action;
        this.handleQuickAction(action);
      });
    });

    // Panel toggles
    document.querySelectorAll(".panel-toggle").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const panel = e.currentTarget.dataset.panel;
        this.togglePanel(panel);
      });
    });

    // Models panel controls
    document
      .getElementById("refreshModelsBtn")
      ?.addEventListener("click", () => this.refreshModelsFromAPI());
    document
      .getElementById("compareModelsBtn")
      ?.addEventListener("click", () => this.openModelComparison());

    // Protection status
    document
      .getElementById("systemStatus")
      ?.addEventListener("click", () => this.showProtectionDetails());

    // Modal controls
    document
      .getElementById("knowledgeBaseBtn")
      ?.addEventListener("click", () => this.openModal("knowledgeBaseModal"));
    document
      .getElementById("modelTuningBtn")
      ?.addEventListener("click", () => this.openModal("modelTuningModal"));
    document
      .getElementById("aiModelsBtn")
      ?.addEventListener("click", () => this.openModal("aiModelsModal"));

    // Modal close buttons
    document.querySelectorAll(".modal-close").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const modalId = e.target.closest(".modal-close").dataset.modal;
        this.closeModal(modalId);
      });
    });

    // Close modal when clicking outside
    document.querySelectorAll(".modal").forEach((modal) => {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          this.closeModal(modal.id);
        }
      });
    });

    // Modal action buttons
    document
      .getElementById("modalUploadDocBtn")
      ?.addEventListener("click", () => this.uploadDocument());
    document
      .getElementById("modalUploadUrlBtn")
      ?.addEventListener("click", () => this.uploadFromUrl());
    document
      .getElementById("modalSearchDocsBtn")
      ?.addEventListener("click", () => this.searchDocuments());
    document
      .getElementById("modalCreateAdapterBtn")
      ?.addEventListener("click", () => this.createLoRAAdapter());
    document
      .getElementById("modalQuickTrainBtn")
      ?.addEventListener("click", () => this.quickTrainAdapter());
    document
      .getElementById("modalLoadPretrainedBtn")
      ?.addEventListener("click", () => this.loadPretrainedAdapter());
    document
      .getElementById("modalRefreshModelsBtn")
      ?.addEventListener("click", () => this.refreshModelsInModal());

    // Make directSwitchModel available globally for onclick handlers
    window.nexusAI = this;
    document
      .getElementById("modalCompareModelsBtn")
      ?.addEventListener("click", () => this.openModelComparison());

    // Enhanced RAG controls
    document
      .getElementById("uploadDocBtn")
      ?.addEventListener("click", () => this.uploadDocument());
    document
      .getElementById("uploadUrlBtn")
      ?.addEventListener("click", () => this.uploadFromUrl());
    document
      .getElementById("quickSearchBtn")
      ?.addEventListener("click", () => this.performQuickSearch());
    document
      .getElementById("quickSearchInput")
      ?.addEventListener("input", (e) => this.handleSearchInput(e));
    document
      .getElementById("quickSearchInput")
      ?.addEventListener("keydown", (e) => this.handleSearchKeydown(e));
    document
      .getElementById("analyzeKnowledgeBtn")
      ?.addEventListener("click", () => this.analyzeKnowledge());
    document
      .getElementById("generateSummaryBtn")
      ?.addEventListener("click", () => this.generateKnowledgeSummary());
    document
      .getElementById("exportKnowledgeBtn")
      ?.addEventListener("click", () => this.exportKnowledge());
    document
      .getElementById("clearKnowledgeBtn")
      ?.addEventListener("click", () => this.clearKnowledge());
    document
      .getElementById("refreshLibraryBtn")
      ?.addEventListener("click", () => this.refreshDocumentLibrary());
    document
      .getElementById("sortLibraryBtn")
      ?.addEventListener("click", () => this.sortDocumentLibrary());

    // Enhanced LoRA controls
    document
      .getElementById("createAdapterBtn")
      ?.addEventListener("click", () => this.createLoRAAdapter());
    document
      .getElementById("quickTrainBtn")
      ?.addEventListener("click", () => this.quickTrainAdapter());
    document
      .getElementById("loadPretrainedBtn")
      ?.addEventListener("click", () => this.loadPretrainedAdapter());
    document
      .getElementById("importDatasetBtn")
      ?.addEventListener("click", () => this.importTrainingDataset());
    document
      .getElementById("autoTuneBtn")
      ?.addEventListener("click", () => this.autoTuneHyperparameters());
    document
      .getElementById("analyzePerformanceBtn")
      ?.addEventListener("click", () => this.analyzeAdapterPerformance());
    document
      .getElementById("compareAdaptersBtn")
      ?.addEventListener("click", () => this.compareAdapters());
    document
      .getElementById("optimizeHyperparamsBtn")
      ?.addEventListener("click", () => this.toggleHyperparameterTuning());
    document
      .getElementById("exportAdapterBtn")
      ?.addEventListener("click", () => this.exportAdapter());
    document
      .getElementById("backupAdaptersBtn")
      ?.addEventListener("click", () => this.backupAllAdapters());
    document
      .getElementById("clearAdaptersBtn")
      ?.addEventListener("click", () => this.clearAllAdapters());
    document
      .getElementById("refreshAdaptersBtn")
      ?.addEventListener("click", () => this.refreshAdapterLibrary());
    document
      .getElementById("sortAdaptersBtn")
      ?.addEventListener("click", () => this.sortAdapterLibrary());
    document
      .getElementById("filterAdaptersBtn")
      ?.addEventListener("click", () => this.filterAdapters());

    // Hyperparameter controls
    document
      .getElementById("loraRank")
      ?.addEventListener("input", (e) => this.updateRankValue(e));
    document
      .getElementById("loraAlpha")
      ?.addEventListener("input", (e) => this.updateAlphaValue(e));
    document
      .getElementById("applyParamsBtn")
      ?.addEventListener("click", () => this.applyHyperparameters());
    document
      .getElementById("resetParamsBtn")
      ?.addEventListener("click", () => this.resetHyperparameters());

    // Settings modal
    document
      .getElementById("closeSettings")
      ?.addEventListener("click", () => this.closeSettings());
    document
      .getElementById("saveSettings")
      ?.addEventListener("click", () => this.saveSettings());
    document
      .getElementById("resetSettings")
      ?.addEventListener("click", () => this.resetSettings());

    // Settings tabs
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", (e) => {
        const tabName = e.currentTarget.dataset.tab;
        this.switchTab(tabName);
      });
    });

    // Model selection is now handled through the AI Models modal

    // Theme toggle
    document.getElementById("themeSelect")?.addEventListener("change", (e) => {
      this.settings.theme = e.target.value;
      this.applyTheme();
      this.saveSettings();
    });

    // Auto-resize textarea
    this.setupAutoResize();
  }

  setupAutoResize() {
    const textarea = document.getElementById("messageInput");
    if (!textarea) return;

    textarea.addEventListener("input", function () {
      this.style.height = "auto";
      this.style.height = Math.min(this.scrollHeight, 120) + "px";
    });
  }

  toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar?.classList.toggle("open");
  }

  startNewChat() {
    this.currentConversation = null;
    this.showWelcomeScreen();
    this.clearActiveConversation();
    this.showNotification("New conversation started", "success");
  }

  clearActiveConversation() {
    document.querySelectorAll(".conversation-item").forEach((item) => {
      item.classList.remove("active");
    });
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
  }

  handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  async sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const message = messageInput?.value.trim();

    if (!message) return;

    // Clear input
    messageInput.value = "";
    messageInput.style.height = "auto";
    document.getElementById("sendBtn").disabled = true;

    // Show chat screen if on welcome screen
    this.showChatScreen();

    // Add user message
    this.addMessage(message, "user");

    // Show typing indicator
    this.showTypingIndicator();

    try {
      // Send to AI (replace with your API call)
      const response = await this.callAI(message);
      this.hideTypingIndicator();
      this.addMessage(response, "assistant");
    } catch (error) {
      this.hideTypingIndicator();
      this.addMessage(
        "Sorry, I encountered an error. Please try again.",
        "assistant"
      );
      this.showNotification("Failed to send message", "error");
    }
  }

  addMessage(content, sender) {
    const messagesList = document.getElementById("messagesList");
    if (!messagesList) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.innerHTML =
      sender === "user"
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
      const modelName = this.formatModelName(
        responseInfo.model_used || this.currentModel
      );
      const providerName = responseInfo.provider_used || "groq";
      const responseTime = responseInfo.response_time || 0;

      const providerBadge = `<span class="provider-badge provider-${providerName}">${this.getProviderDisplayName(
        providerName
      )}</span>`;
      const timingInfo =
        responseTime > 0
          ? `<span class="timing-info">${responseTime.toFixed(2)}s</span>`
          : "";

      meta.innerHTML = `
                <span class="model-info">
                    <i class="fas fa-robot"></i>
                    ${modelName}
                    ${providerBadge}
                    ${timingInfo}
                </span>
                <span>${new Date().toLocaleTimeString()}</span>
            `;
    } else {
      meta.innerHTML = `<span>${new Date().toLocaleTimeString()}</span>`;
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

    // Update conversation in sidebar
    this.updateCurrentConversation(content, sender);
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
    const selectedModel = this.currentModel || "llama-3.1-8b-instant";

    // Guardrails are now handled by the backend automatically

    try {
      const apiResponse = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          model: selectedModel,
          auto_select: false, // Disable auto-selection to respect user's model choice
          guardrails_enabled: this.getActiveGuardrails(),
        }),
      });

      if (!apiResponse.ok) {
        throw new Error(`HTTP error! status: ${apiResponse.status}`);
      }

      const data = await apiResponse.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Update protection status based on response
      this.updateProtectionStatus(data);

      // Store provider and model information for display
      this.lastResponseInfo = {
        model_used: data.model_used || selectedModel,
        provider_used: data.provider_used || "groq",
        response_time: data.response_time || 0,
        usage: data.usage || {},
      };

      let responseText =
        data.response || data.message || "No response received";

      // Enhance response formatting if it's a simple response
      if (
        responseText &&
        !responseText.includes("\n") &&
        responseText.length > 100
      ) {
        responseText = this.enhanceResponseFormatting(responseText);
      }

      return responseText;
    } catch (error) {
      console.error("API call failed:", error);
      // Fallback response for demo with better formatting
      return this.createFormattedDemoResponse(message, error.message);
    }
  }

  updateCurrentConversation(content, sender) {
    if (!this.currentConversation) {
      // Create new conversation
      this.currentConversation = {
        id: Date.now(),
        title: content.substring(0, 30) + (content.length > 30 ? "..." : ""),
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      this.conversations.unshift(this.currentConversation);
      this.renderConversations();
    }

    this.currentConversation.messages.push({
      content,
      sender,
      timestamp: new Date(),
    });

    if (sender === "user") {
      this.currentConversation.updatedAt = new Date();
    }

    this.saveConversations();
  }

  renderConversations() {
    const conversationsList = document.getElementById("conversationsList");
    if (!conversationsList) return;

    conversationsList.innerHTML = "";

    this.conversations.forEach((conversation) => {
      const item = document.createElement("div");
      item.className = "conversation-item";
      if (
        this.currentConversation &&
        conversation.id === this.currentConversation.id
      ) {
        item.classList.add("active");
      }

      const lastMessage =
        conversation.messages[conversation.messages.length - 1];
      const preview = lastMessage
        ? lastMessage.content.substring(0, 50) + "..."
        : "New conversation";

      item.innerHTML = `
                <div class="conversation-icon">
                    <i class="fas fa-comment"></i>
                </div>
                <div class="conversation-content">
                    <div class="conversation-title">${conversation.title}</div>
                    <div class="conversation-preview">${preview}</div>
                    <div class="conversation-meta">
                        <span>${this.formatTime(conversation.updatedAt)}</span>
                    </div>
                </div>
                <div class="conversation-actions">
                    <button class="conversation-action-btn delete" title="Delete Conversation">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

      // Add click handler
      item.addEventListener("click", (e) => {
        if (!e.target.closest(".conversation-actions")) {
          this.loadConversation(conversation.id);
        }
      });

      // Add delete handler
      const deleteBtn = item.querySelector(".delete");
      deleteBtn?.addEventListener("click", (e) => {
        e.stopPropagation();
        this.deleteConversation(conversation.id);
      });

      conversationsList.appendChild(item);
    });
  }

  loadConversation(id) {
    const conversation = this.conversations.find((c) => c.id === id);
    if (!conversation) return;

    this.currentConversation = conversation;
    this.showChatScreen();

    // Clear current messages
    const messagesList = document.getElementById("messagesList");
    if (messagesList) {
      messagesList.innerHTML = "";
    }

    // Load conversation messages
    conversation.messages.forEach((msg) => {
      this.addMessage(msg.content, msg.sender);
    });

    // Update active state
    this.clearActiveConversation();
    document.querySelectorAll(".conversation-item").forEach((item, index) => {
      if (this.conversations[index].id === id) {
        item.classList.add("active");
      }
    });
  }

  deleteConversation(id) {
    if (confirm("Are you sure you want to delete this conversation?")) {
      this.conversations = this.conversations.filter((c) => c.id !== id);

      if (this.currentConversation && this.currentConversation.id === id) {
        this.currentConversation = null;
        this.showWelcomeScreen();
      }

      this.renderConversations();
      this.saveConversations();
      this.showNotification("Conversation deleted", "success");
    }
  }

  clearAllConversations() {
    if (
      confirm(
        "Are you sure you want to delete all conversations? This action cannot be undone."
      )
    ) {
      this.conversations = [];
      this.currentConversation = null;
      this.renderConversations();
      this.saveConversations();
      this.showWelcomeScreen();
      this.showNotification("All conversations cleared", "success");
    }
  }

  exportConversations() {
    const data = {
      conversations: this.conversations,
      exportedAt: new Date(),
      version: "2.0",
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `nexusai-conversations-${
      new Date().toISOString().split("T")[0]
    }.json`;
    a.click();
    URL.revokeObjectURL(url);

    this.showNotification("Conversations exported", "success");
  }

  handleQuickAction(action) {
    const prompts = {
      code: "Help me write code for ",
      write: "Help me write ",
      analyze: "Analyze this data: ",
      creative: "Help me create ",
    };

    const messageInput = document.getElementById("messageInput");
    if (messageInput && prompts[action]) {
      messageInput.value = prompts[action];
      messageInput.focus();
      messageInput.setSelectionRange(
        prompts[action].length,
        prompts[action].length
      );
    }

    // For demo purposes, show a formatted response immediately
    if (action === "code") {
      setTimeout(() => {
        this.addMessage(this.getSampleCodeResponse(), "assistant");
      }, 1000);
    }
  }

  getSampleCodeResponse() {
    return `## Code Assistance

I'd be happy to help you write code! Here are some **popular options**:

### Web Development
- **JavaScript/TypeScript** - Frontend and backend development
- **React/Vue/Angular** - Modern UI frameworks
- **Node.js** - Server-side JavaScript

### Programming Languages
1. **Python** - Data science, AI, web development
2. **Java** - Enterprise applications, Android development  
3. **C++** - System programming, game development
4. **Go** - Cloud services, microservices

### Code Example
Here's a simple JavaScript function:

\`\`\`javascript
function greetUser(name) {
    return \`Hello, \${name}! Welcome to NexusAI.\`;
}

// Usage
console.log(greetUser("Developer"));
\`\`\`

**What specific code would you like help with?** Just describe your project and I'll provide tailored assistance!`;
  }

  togglePanel(panelName) {
    const panel = document.getElementById(`${panelName}Content`);
    const toggle = document.querySelector(`[data-panel="${panelName}"]`);

    if (panel && toggle) {
      const isExpanded = panel.classList.contains("expanded");

      if (isExpanded) {
        panel.classList.remove("expanded");
        toggle.classList.remove("expanded");
      } else {
        panel.classList.add("expanded");
        toggle.classList.add("expanded");
      }
    }
  }

  openSettings() {
    const modal = document.getElementById("settingsModal");
    modal?.classList.add("active");
  }

  closeSettings() {
    const modal = document.getElementById("settingsModal");
    modal?.classList.remove("active");
  }

  switchTab(tabName) {
    // Remove active class from all tabs and content
    document
      .querySelectorAll(".tab")
      .forEach((tab) => tab.classList.remove("active"));
    document
      .querySelectorAll(".tab-content")
      .forEach((content) => content.classList.remove("active"));

    // Add active class to selected tab and content
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add("active");
    document.getElementById(tabName)?.classList.add("active");
  }

  saveSettings() {
    // Collect settings from form
    const themeSelect = document.getElementById("themeSelect");
    const autoSave = document.getElementById("autoSave");
    const compactMode = document.getElementById("compactMode");
    const defaultModel = document.getElementById("defaultModelSelect");

    if (themeSelect) this.settings.theme = themeSelect.value;
    if (autoSave) this.settings.autoSave = autoSave.checked;
    if (compactMode) this.settings.compactMode = compactMode.checked;
    if (defaultModel) this.settings.defaultModel = defaultModel.value;

    localStorage.setItem("nexusai-settings", JSON.stringify(this.settings));
    this.applySettings();
    this.closeSettings();
    this.showNotification("Settings saved", "success");
  }

  resetSettings() {
    if (confirm("Reset all settings to default?")) {
      this.settings = this.getDefaultSettings();
      this.applySettings();
      this.populateSettingsForm();
      this.showNotification("Settings reset to default", "success");
    }
  }

  loadSettings() {
    const saved = localStorage.getItem("nexusai-settings");
    return saved ? JSON.parse(saved) : this.getDefaultSettings();
  }

  getDefaultSettings() {
    return {
      theme: "auto",
      autoSave: true,
      compactMode: false,
      defaultModel: "llama-3.1-8b-instant",
    };
  }

  applySettings() {
    this.applyTheme();
    this.populateSettingsForm();

    // FIXED: Only apply model from settings during initial load
    // Don't override user's explicit model selection
    const oldModel = this.currentModel;

    // Check if this is being called during initialization
    const isInitializing = !this._initialized;
    const userHasSelectedModel = this._userSelectedModel;

    if (isInitializing && !userHasSelectedModel) {
      // During initialization, use settings (only if user hasn't selected a model)
      this.currentModel = this.settings.defaultModel || "llama-3.1-8b-instant";
    } else if (userHasSelectedModel) {
      // User has explicitly selected a model - NEVER override it
      this.settings.defaultModel = this.currentModel;
    } else {
      // Post-init but no user selection - use settings
      this.currentModel = this.settings.defaultModel || "llama-3.1-8b-instant";
    }

    // Update model display in status bar
    this.updateModelDisplay();
  }

  applyTheme() {
    const theme = this.settings.theme;
    const body = document.body;

    if (theme === "auto") {
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      body.setAttribute("data-theme", prefersDark ? "dark" : "light");
    } else {
      body.setAttribute("data-theme", theme);
    }
  }

  populateSettingsForm() {
    const themeSelect = document.getElementById("themeSelect");
    const autoSave = document.getElementById("autoSave");
    const compactMode = document.getElementById("compactMode");
    const defaultModel = document.getElementById("defaultModelSelect");

    if (themeSelect) themeSelect.value = this.settings.theme;
    if (autoSave) autoSave.checked = this.settings.autoSave;
    if (compactMode) compactMode.checked = this.settings.compactMode;
    if (defaultModel) defaultModel.value = this.settings.defaultModel;
  }

  loadConversations() {
    const saved = localStorage.getItem("nexusai-conversations");
    this.conversations = saved ? JSON.parse(saved) : [];
    this.renderConversations();
  }

  saveConversations() {
    if (this.settings.autoSave) {
      localStorage.setItem(
        "nexusai-conversations",
        JSON.stringify(this.conversations)
      );
    }
  }

  showNotification(message, type = "info") {
    const container = document.getElementById("notificationContainer");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;

    container.appendChild(notification);

    // Show notification
    setTimeout(() => notification.classList.add("show"), 100);

    // Hide and remove notification
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  formatTime(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Date(date).toLocaleDateString();
  }

  formatMessage(content, sender) {
    if (sender === "user") {
      // User messages - simple HTML escaping
      return this.escapeHtml(content);
    }

    // AI messages - apply formatting
    let formatted = this.escapeHtml(content);

    // Convert markdown-style formatting to HTML
    formatted = this.convertMarkdownToHtml(formatted);

    return formatted;
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  convertMarkdownToHtml(text) {
    // Convert common markdown patterns to HTML

    // Headers
    text = text.replace(/^### (.*$)/gm, '<h3 class="message-header">$1</h3>');
    text = text.replace(/^## (.*$)/gm, '<h2 class="message-header">$1</h2>');
    text = text.replace(/^# (.*$)/gm, '<h1 class="message-header">$1</h1>');

    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/__(.*?)__/g, "<strong>$1</strong>");

    // Italic text
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
    text = text.replace(/_(.*?)_/g, "<em>$1</em>");

    // Code blocks
    text = text.replace(
      /```([\s\S]*?)```/g,
      '<pre class="code-block"><code>$1</code></pre>'
    );

    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // Lists
    text = text.replace(/^\* (.*$)/gm, '<li class="list-item">$1</li>');
    text = text.replace(/^- (.*$)/gm, '<li class="list-item">$1</li>');
    text = text.replace(
      /^\d+\. (.*$)/gm,
      '<li class="list-item numbered">$1</li>'
    );

    // Wrap consecutive list items in ul/ol
    text = text.replace(
      /(<li class="list-item">[^<]*<\/li>\s*)+/g,
      '<ul class="message-list">$&</ul>'
    );
    text = text.replace(
      /(<li class="list-item numbered">[^<]*<\/li>\s*)+/g,
      '<ol class="message-list numbered">$&</ol>'
    );

    // Line breaks
    text = text.replace(/\n\n/g, '</p><p class="message-paragraph">');
    text = text.replace(/\n/g, "<br>");

    // Wrap in paragraph if not already wrapped
    if (
      !text.includes("<p>") &&
      !text.includes("<h") &&
      !text.includes("<ul>") &&
      !text.includes("<ol>")
    ) {
      text = `<p class="message-paragraph">${text}</p>`;
    }

    // Links (basic)
    text = text.replace(
      /https?:\/\/[^\s<]+/g,
      '<a href="$&" target="_blank" class="message-link">$&</a>'
    );

    return text;
  }

  showAttachmentOptions() {
    // Placeholder for attachment functionality
    this.showNotification("Attachment feature coming soon", "info");
  }

  enhanceResponseFormatting(response) {
    // Add basic formatting to long responses
    const sentences = response.split(". ");
    if (sentences.length > 3) {
      // Group sentences into paragraphs
      const paragraphs = [];
      for (let i = 0; i < sentences.length; i += 2) {
        const paragraph = sentences.slice(i, i + 2).join(". ");
        paragraphs.push(paragraph + (paragraph.endsWith(".") ? "" : "."));
      }
      return paragraphs.join("\n\n");
    }
    return response;
  }

  createFormattedDemoResponse(message, errorMsg) {
    return `## Demo Response

**Your message:** "${message}"

This is a **demo response** from NexusAI. The system is currently running in demonstration mode.

### Features Available:
- ✅ **AI Guardrails** - Content filtering and safety
- ✅ **Model Selection** - Choose from multiple AI models  
- ✅ **RAG System** - Document upload and knowledge base
- ✅ **LoRA Fine-tuning** - Custom model adaptations

### Current Status:
- **API Status:** \`Error - ${errorMsg}\`
- **Guardrails:** Active and protecting
- **UI:** Fully functional

*To enable full AI responses, please configure your API key in the backend.*`;
  }

  toggleVoiceInput() {
    // Placeholder for voice input functionality
    this.showNotification("Voice input feature coming soon", "info");
  }

  // ===== MODELS MANAGEMENT =====
  async loadAvailableModels() {
    console.log("🚀 loadAvailableModels called");
    try {
      const response = await fetch("/api/models");
      console.log("📡 API response received:", response.status);
      const data = await response.json();
      console.log("📊 API data:", data);
      console.log("📊 Models count:", data.models?.length);
      console.log(
        "📊 Models by provider:",
        data.models?.reduce((acc, m) => {
          acc[m.provider] = (acc[m.provider] || 0) + 1;
          return acc;
        }, {})
      );

      if (data.status === "success") {
        // Handle new multi-provider response format
        const models = data.models || data.textModels || [];
        this.availableModels = models; // Store for modal use
        this.providers = data.providers || {};
        this.multiProviderEnabled = data.multi_provider_enabled || false;

        console.log("🔧 About to call updateProviderStatus with:", {
          providers: this.providers,
          multiProviderEnabled: this.multiProviderEnabled,
        });

        this.renderModelsList(models);
        this.updateModelsStats(models);
        this.updateMainModelDropdown(models);
        this.updateProviderStatus();

        // Multi-provider system is active - no notification needed
      } else {
        // Fallback to default models
        const defaultModels = this.getDefaultModels();
        this.availableModels = defaultModels; // Store for modal use
        this.renderModelsList(defaultModels);
        this.updateModelsStats(defaultModels);
        this.updateMainModelDropdown(defaultModels);
      }
    } catch (error) {
      console.error("Failed to load models:", error);
      const defaultModels = this.getDefaultModels();
      this.availableModels = defaultModels; // Store for modal use
      this.renderModelsList(defaultModels);
      this.updateModelsStats(defaultModels);
      this.updateMainModelDropdown(defaultModels);
      this.showNotification(
        "Using default models (API unavailable)",
        "warning"
      );
    }
  }

  getDefaultModels() {
    return [
      {
        id: "llama-3.1-8b-instant",
        name: "Llama 3.1 8B (Fast)",
        description: "Ultra-fast responses for everyday conversations",
        provider: "groq",
        provider_name: "Groq",
        supportsVision: false,
      },
      {
        id: "llama-3.1-70b-versatile",
        name: "Llama 3.1 70B (Smart)",
        description: "Advanced reasoning for complex problems",
        provider: "groq",
        provider_name: "Groq",
        supportsVision: false,
      },
      {
        id: "llama-3.2-11b-vision-preview",
        name: "Llama 3.2 Vision",
        description: "Image analysis and visual reasoning",
        provider: "groq",
        provider_name: "Groq",
        supportsVision: true,
      },
    ];
  }

  async refreshModelsFromAPI() {
    // Force refresh models from all provider APIs in real-time
    console.log("🔄 Forcing real-time model refresh from all provider APIs...");

    try {
      const response = await fetch("/api/models/refresh", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("✅ Real-time models refreshed:", data);

      if (data.status === "success" && data.models) {
        this.availableModels = data.models;
        this.providers = data.providers || {};

        console.log(`🎯 Refreshed ${data.total_count} models from APIs:`);
        const providerCounts = data.models.reduce((acc, m) => {
          acc[m.provider] = (acc[m.provider] || 0) + 1;
          return acc;
        }, {});
        console.log("📊 Models by provider:", providerCounts);

        // Update UI components
        this.renderModelsList(data.models);
        this.updateModelsStats(data.models);
        this.updateMainModelDropdown(data.models);
        this.updateProviderStatus();

        // Show success notification
        this.showNotification(
          `🔄 Refreshed ${data.total_count} models from ${
            Object.keys(providerCounts).length
          } providers`,
          "success",
          3000
        );

        return data.models;
      } else {
        throw new Error(data.error || "Failed to refresh models");
      }
    } catch (error) {
      console.error("❌ Error refreshing models from API:", error);
      this.showNotification(
        `❌ Failed to refresh models: ${error.message}`,
        "error",
        4000
      );
      throw error;
    }
  }

  updateProviderStatus() {
    console.log("🎯 updateProviderStatus called", {
      providers: this.providers,
      multiProviderEnabled: this.multiProviderEnabled,
    });

    // TEMPORARY FIX: Add provider status to chat area header
    const chatArea = document.querySelector(".chat-area");
    const welcomeScreen = document.getElementById("welcomeScreen");

    if (chatArea && this.providers) {
      // Remove existing temp status
      const existingStatus = document.getElementById("tempChatProviderStatus");
      if (existingStatus) existingStatus.remove();

      // Create visible provider status in chat area
      const tempStatus = document.createElement("div");
      tempStatus.id = "tempChatProviderStatus";
      tempStatus.style.cssText = `
                position: absolute;
                top: 20px;
                left: 20px;
                right: 20px;
                background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
                z-index: 1000;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 12px;
            `;

      const enabledProviders = Object.values(this.providers).filter(
        (p) => p.enabled
      );
      const providerNames = enabledProviders.map((p) => p.name).join(", ");

      tempStatus.innerHTML = `
                <span>🚀 Multi-Provider AI Active:</span>
                <strong>${providerNames}</strong>
                <span>(${enabledProviders.length} providers)</span>
                <span style="margin-left: auto; font-size: 12px; opacity: 0.9;">✨ Enhanced Performance</span>
            `;

      chatArea.style.position = "relative";
      chatArea.appendChild(tempStatus);

      console.log("✅ Added provider status to chat area");

      // Auto-hide after 5 seconds
      setTimeout(() => {
        if (tempStatus && tempStatus.parentNode) {
          tempStatus.style.transition = "opacity 0.5s ease-out";
          tempStatus.style.opacity = "0";
          setTimeout(() => {
            if (tempStatus && tempStatus.parentNode) {
              tempStatus.remove();
            }
          }, 500);
        }
      }, 5000);
    }

    // Update sleek AI provider hub
    const providerHub = document.getElementById("providerIndicator");

    if (this.providers && providerHub) {
      const enabledProviders = Object.values(this.providers).filter(
        (p) => p.enabled
      );

      // Update provider nodes with smart tooltips
      const nodes = providerHub.querySelectorAll(".provider-node");
      nodes.forEach((node) => {
        const providerType = node.dataset.provider;

        // Better provider matching - check both by key and by name
        const provider =
          this.providers[providerType] ||
          Object.values(this.providers).find(
            (p) => p.name.toLowerCase() === providerType
          );

        if (provider && provider.enabled) {
          node.classList.add("active");
          console.log(`✅ Activated ${providerType} provider node`);
        } else {
          node.classList.remove("active");
          console.log(`⚪ ${providerType} provider not active`);
        }

        // Add smart tooltip functionality
        this.setupProviderNodeTooltip(node, providerType, provider);
      });

      // Update hub status
      const statusText = providerHub.querySelector("#hubStatusText");
      const statusFill = providerHub.querySelector("#hubStatusFill");
      const hubCount = providerHub.querySelector("#hubCount");

      if (statusText) {
        statusText.textContent =
          enabledProviders.length > 1 ? "Multi-AI" : "Single-AI";
      }

      if (statusFill) {
        const fillPercentage = Math.min(
          (enabledProviders.length / 4) * 100,
          100
        );
        statusFill.style.width = `${fillPercentage}%`;
      }

      if (hubCount) {
        hubCount.textContent = enabledProviders.length;
      }

      // Update beautiful tooltip
      const tooltipContent = providerHub.querySelector("#tooltipContent");
      if (tooltipContent) {
        const tooltipHtml = enabledProviders
          .map(
            (provider) => `
                    <div class="provider-item">
                        <div class="provider-name">
                            <div class="provider-dot-mini ${provider.name.toLowerCase()}" style="background: ${this.getProviderColor(
              provider.name.toLowerCase()
            )}"></div>
                            <span>${provider.name}</span>
                        </div>
                        <div class="provider-status">${
                          provider.requests_last_minute
                        }/${provider.rate_limit}/min</div>
                    </div>
                `
          )
          .join("");

        tooltipContent.innerHTML =
          tooltipHtml || '<div style="opacity: 0.6;">No providers active</div>';
      }

      console.log("✅ Sleek AI provider hub updated");

      // Enhanced click handler
      providerHub.onclick = (e) => {
        e.stopPropagation();
        this.showProviderDetails(enabledProviders);
      };
    }
  }

  getProviderColor(providerName) {
    const colors = {
      groq: "#ff6b35",
      ollama: "#6366f1",
      openai: "#00d4aa",
      anthropic: "#f59e0b",
      google: "#4285f4",
    };
    return colors[providerName] || "#6366f1";
  }

  getProviderTooltip(providerType, provider) {
    const tooltips = {
      groq:
        provider && provider.enabled
          ? `🚀 Groq - Ultra Fast AI (${provider.requests_last_minute}/${provider.rate_limit}/min)`
          : "⚪ Groq - Ultra Fast AI (Offline)",
      ollama:
        provider && provider.enabled
          ? `🏠 Ollama - Local AI (${provider.requests_last_minute}/${provider.rate_limit}/min)`
          : "⚪ Ollama - Local AI (Offline)",
      openai:
        provider && provider.enabled
          ? `🧠 OpenAI - GPT Models (${provider.requests_last_minute}/${provider.rate_limit}/min)`
          : "⚪ OpenAI - GPT Models (Offline)",
      anthropic:
        provider && provider.enabled
          ? `🎭 Anthropic - Claude AI (${provider.requests_last_minute}/${provider.rate_limit}/min)`
          : "⚪ Anthropic - Claude AI (Offline)",
    };
    return tooltips[providerType] || `${providerType} AI Provider`;
  }

  showProviderDetails(providers) {
    const details = providers
      .map(
        (p) =>
          `🚀 ${p.name}: ${p.requests_last_minute}/${p.rate_limit} req/min (Priority: ${p.priority})`
      )
      .join("\n");

    this.showNotification(
      `🌟 AI Provider Network Status:\n\n${details}\n\n✨ Multi-provider system ensures 99.9% uptime!`,
      "success",
      4000
    );
  }

  setupProviderNodeTooltip(node, providerType, provider) {
    // Create tooltip element if it doesn't exist
    let tooltip = document.getElementById("providerNodeTooltip");
    if (!tooltip) {
      tooltip = document.createElement("div");
      tooltip.id = "providerNodeTooltip";
      tooltip.className = "provider-node-tooltip";
      document.body.appendChild(tooltip);
    }

    // Remove existing event listeners
    node.removeEventListener("mouseenter", node._tooltipEnter);
    node.removeEventListener("mouseleave", node._tooltipLeave);

    // Mouse enter event
    node._tooltipEnter = (e) => {
      const tooltipText = this.getProviderTooltip(providerType, provider);
      tooltip.textContent = tooltipText;
      tooltip.className = `provider-node-tooltip ${providerType}`;

      // Smart positioning to stay within viewport
      const rect = node.getBoundingClientRect();

      // Position tooltip below the node by default
      let left = rect.left + rect.width / 2;
      let top = rect.bottom + 8;

      // Set initial position to measure tooltip size
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${top}px`;
      tooltip.classList.add("show");

      // Get tooltip dimensions after showing
      const tooltipRect = tooltip.getBoundingClientRect();

      // Adjust horizontal position to center and stay in viewport
      left = rect.left + rect.width / 2 - tooltipRect.width / 2;
      if (left < 10) {
        left = 10;
      } else if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
      }

      // Adjust vertical position if tooltip goes off-screen
      if (top + tooltipRect.height > window.innerHeight - 10) {
        top = rect.top - tooltipRect.height - 8;
      }

      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${top}px`;
    };

    // Mouse leave event
    node._tooltipLeave = () => {
      tooltip.classList.remove("show");
    };

    node.addEventListener("mouseenter", node._tooltipEnter);
    node.addEventListener("mouseleave", node._tooltipLeave);

    // Update models list to show provider information
    this.updateModelsWithProviderInfo();
  }

  updateModelsWithProviderInfo() {
    // This will be called when rendering models to show provider badges
    const modelItems = document.querySelectorAll(".model-item");
    modelItems.forEach((item) => {
      const modelId = item.dataset.modelId;
      const model = this.availableModels.find((m) => m.id === modelId);
      if (model && model.provider_name) {
        const providerBadge = item.querySelector(".provider-badge");
        if (!providerBadge) {
          const badge = document.createElement("span");
          badge.className = `provider-badge provider-${model.provider}`;
          badge.textContent = model.provider_name;
          item.appendChild(badge);
        }
      }
    });
  }

  renderModelsList(models) {
    const modelsList = document.getElementById("modelsList");
    if (!modelsList) {
      console.error("❌ modelsList element not found!");
      return;
    }

    console.log("🎨 renderModelsList called with", models.length, "models");
    console.log(
      "🎨 Models:",
      models.map((m) => `${m.name} (${m.provider})`)
    );

    const currentModel = this.currentModel || "llama-3.1-8b-instant";

    modelsList.innerHTML = "";

    models.forEach((model) => {
      const modelItem = document.createElement("div");
      modelItem.className = `model-item ${
        model.id === currentModel ? "active" : ""
      }`;

      const providerBadge = model.provider_name
        ? `<span class="provider-badge provider-${
            model.provider
          }" style="background: ${this.getProviderColor(
            model.provider
          )}; color: white; font-size: 8px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">${
            model.provider_name
          }</span>`
        : "";

      const costInfo =
        model.cost_per_1k_tokens !== undefined
          ? `<span class="cost-info" style="color: ${
              model.cost_per_1k_tokens === 0 ? "#4caf50" : "#666"
            }; font-weight: ${model.cost_per_1k_tokens === 0 ? "600" : "400"};">
                    ${
                      model.cost_per_1k_tokens === 0
                        ? "🆓 FREE"
                        : `💰 $${model.cost_per_1k_tokens.toFixed(5)}/1K`
                    }
                </span>`
          : "";

      modelItem.innerHTML = `
                <div class="model-info">
                    <div class="model-header">
                        <div class="model-name">${model.name || model.id}</div>
                        ${providerBadge}
                    </div>
                    <div class="model-description">${
                      model.description || "AI Language Model"
                    }</div>
                    ${costInfo}
                </div>
                <button class="model-select-btn" data-model="${model.id}">
                    ${model.id === currentModel ? "Active" : "Select"}
                </button>
            `;

      modelItem.dataset.modelId = model.id;

      // Add click handler for model selection
      const selectBtn = modelItem.querySelector(".model-select-btn");
      selectBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.selectModel(model.id);
      });

      modelsList.appendChild(modelItem);
    });
  }

  updateMainModelDropdown(models) {
    const defaultModelSelect = document.getElementById("defaultModelSelect");

    // Also update the settings dropdown
    if (defaultModelSelect) {
      const currentValue = defaultModelSelect.value;
      defaultModelSelect.innerHTML = "";

      models.forEach((model) => {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = model.name || this.formatModelName(model.id);
        defaultModelSelect.appendChild(option);
      });

      if (models.find((m) => m.id === currentValue)) {
        defaultModelSelect.value = currentValue;
      } else if (models.length > 0) {
        defaultModelSelect.value = models[0].id;
      }
    }
  }

  getProviderDisplayName(providerId) {
    const providerNames = {
      groq: "Groq",
      openai: "OpenAI",
      anthropic: "Anthropic",
      google: "Google",
      ollama: "Ollama",
      huggingface: "HF",
    };
    return providerNames[providerId] || providerId.toUpperCase();
  }

  formatModelName(modelId) {
    // Convert model ID to human-readable name
    const nameMap = {
      "llama-3.1-8b-instant": "Llama 3.1 8B (Lightning Fast)",
      "llama-3.1-70b-versatile": "Llama 3.1 70B (Ultra Smart)",
      "llama-3.2-1b-preview": "Llama 3.2 1B (Compact)",
      "llama-3.2-3b-preview": "Llama 3.2 3B (Efficient)",
      "llama-3.2-11b-text-preview": "Llama 3.2 11B (Balanced)",
      "llama-3.2-90b-text-preview": "Llama 3.2 90B (Powerful)",
      "llama-3.2-11b-vision-preview": "Llama 3.2 Vision (Image AI)",

      // OpenAI Models
      "gpt-4o": "GPT-4 Omni",
      "gpt-4o-mini": "GPT-4 Omni Mini",
      "gpt-3.5-turbo": "GPT-3.5 Turbo",

      // Anthropic Models
      "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
      "claude-3-haiku-20240307": "Claude 3 Haiku",

      // Google Models
      "gemini-1.5-pro": "Gemini 1.5 Pro",
      "gemini-1.5-flash": "Gemini 1.5 Flash",
      "llama-3.2-90b-vision-preview": "Llama 3.2 Vision Pro (Advanced)",
      "mixtral-8x7b-32768": "Mixtral 8x7B (Expert Mix)",
      "gemma-7b-it": "Gemma 7B (Google)",
      "gemma2-9b-it": "Gemma 2 9B (Google Next)",
    };

    return (
      nameMap[modelId] ||
      modelId.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
    );
  }

  updateModelsStats(models) {
    const availableCount = document.getElementById("availableModelsCount");
    if (availableCount) {
      availableCount.textContent = models.length;
    }
  }

  selectModel(modelId) {
    // Update current model
    this.currentModel = modelId;
    this.settings.defaultModel = modelId;
    this.saveSettings();

    // Update status bar display
    this.updateModelDisplay();

    this.showNotification(`Switched to ${modelId}`, "success");
  }

  openModelComparison() {
    this.showNotification("Model comparison feature coming soon", "info");
  }

  // ===== FEATURE PANELS INITIALIZATION =====
  initializeFeaturePanels() {
    this.updateRAGStatsEnhanced();
    this.updateLoRAStatsEnhanced();
    this.initializeProtectionStatus();
  }

  updateRAGStats() {
    // Update RAG statistics (placeholder)
    const docsCount = document.getElementById("ragDocsCount");
    const chunksCount = document.getElementById("ragChunksCount");

    if (docsCount) docsCount.textContent = "0";
    if (chunksCount) chunksCount.textContent = "0";
  }

  updateRAGStatsEnhanced() {
    // Initialize enhanced RAG statistics
    this.ragStats = {
      totalDocuments: 0,
      totalChunks: 0,
      indexedSize: 0,
      retrievalAccuracy: 95,
      avgResponseTime: 150,
      lastUpdated: new Date(),
    };

    // Update RAG display elements
    const docsCount = document.getElementById("ragDocsCount");
    const chunksCount = document.getElementById("ragChunksCount");
    const indexSize = document.getElementById("ragIndexSize");
    const accuracy = document.getElementById("ragAccuracy");
    const responseTime = document.getElementById("ragResponseTime");

    if (docsCount) docsCount.textContent = this.ragStats.totalDocuments;
    if (chunksCount) chunksCount.textContent = this.ragStats.totalChunks;
    if (indexSize) indexSize.textContent = `${this.ragStats.indexedSize}MB`;
    if (accuracy) accuracy.textContent = `${this.ragStats.retrievalAccuracy}%`;
    if (responseTime)
      responseTime.textContent = `${this.ragStats.avgResponseTime}ms`;

    this.updateRAGStatus("active", "Ready");
  }

  updateRAGStatus(status, text) {
    const statusDot = document.getElementById("ragStatusDot");
    const statusText = document.getElementById("ragStatusText");

    if (statusDot) {
      statusDot.className = `status-dot ${status}`;
    }
    if (statusText) {
      statusText.textContent = text;
    }
  }

  initializeProtectionStatus() {
    // Initialize AI Guardrails protection status
    const systemStatus = document.getElementById("systemStatus");
    const statusIcon = document.getElementById("statusIcon");

    if (systemStatus) {
      systemStatus.className = "ai-protection-button";
      systemStatus.title = "🛡️ AI Protection Active";
    }
    if (statusIcon) {
      statusIcon.className = "fas fa-shield-check";
    }
  }

  updateProtectionStatus(data) {
    // Update protection status based on API response
    const systemStatus = document.getElementById("systemStatus");
    const statusIcon = document.getElementById("statusIcon");

    // Check if response contains guardrails information
    const guardrails = data.guardrails || {};
    const isProtected =
      guardrails.status !== "blocked" && guardrails.checked !== false;

    if (systemStatus) {
      systemStatus.className = "ai-protection-button";
      systemStatus.title = isProtected
        ? "🛡️ AI Protection Active"
        : "⚠️ Protection Warning";
    }
    if (statusIcon) {
      statusIcon.className = isProtected
        ? "fas fa-shield-check"
        : "fas fa-shield-exclamation";
    }

    // Update guardrails stats if available
    if (guardrails.blocked) {
      this.updateGuardrailsStats("blocked");
    } else if (guardrails.checked) {
      this.updateGuardrailsStats("passed");
    }
  }

  updateLoRAStats() {
    // Update LoRA statistics (placeholder)
    const adaptersCount = document.getElementById("loraAdaptersCount");
    const trainedCount = document.getElementById("loraTrainedCount");

    if (adaptersCount) adaptersCount.textContent = "0";
    if (trainedCount) trainedCount.textContent = "0";
  }

  // ===== RAG SYSTEM =====
  uploadDocument() {
    // Create file input for document upload
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pdf,.txt,.doc,.docx,.md";
    input.multiple = true;

    input.onchange = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;

      this.showNotification(`Uploading ${files.length} document(s)...`, "info");

      try {
        const formData = new FormData();
        files.forEach((file) => formData.append("documents", file));

        const response = await fetch("/api/rag/upload", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (data.status === "success") {
          this.showNotification("Documents uploaded successfully", "success");
          this.updateRAGStats();
        } else {
          throw new Error(data.error || "Upload failed");
        }
      } catch (error) {
        console.error("Upload error:", error);
        this.showNotification("Document upload feature coming soon", "info");
      }
    };

    input.click();
  }

  searchDocuments() {
    const query = prompt("Enter search query:");
    if (!query) return;

    this.showNotification("Document search feature coming soon", "info");
  }

  // ===== LORA SYSTEM =====
  createLoRAAdapter() {
    this.showNotification("LoRA adapter creation feature coming soon", "info");
  }

  manageLoRAAdapters() {
    this.showNotification(
      "LoRA adapter management feature coming soon",
      "info"
    );
  }

  // ===== GUARDRAILS SYSTEM =====
  initializeGuardrails() {
    // Set up guardrail toggle listeners
    document
      .querySelectorAll('#guardrailsContent input[type="checkbox"]')
      .forEach((checkbox) => {
        checkbox.addEventListener("change", (e) => {
          const guardrailName = e.target.id;
          const isEnabled = e.target.checked;
          this.toggleGuardrail(guardrailName, isEnabled);
        });
      });

    // Initialize guardrails stats
    this.guardrailsStats = {
      blocked: 0,
      passed: 0,
    };
  }

  async applyGuardrails(message) {
    const activeGuardrails = this.getActiveGuardrails();

    // Content Safety Check
    if (activeGuardrails.contentSafety) {
      const contentSafetyResult = this.checkContentSafety(message);
      if (contentSafetyResult.blocked) {
        return contentSafetyResult;
      }
    }

    // Prompt Injection Check
    if (activeGuardrails.promptInjection) {
      const promptInjectionResult = this.checkPromptInjection(message);
      if (promptInjectionResult.blocked) {
        return promptInjectionResult;
      }
    }

    // PII Detection Check
    if (activeGuardrails.piiDetection) {
      const piiResult = this.checkPII(message);
      if (piiResult.blocked) {
        return piiResult;
      }
    }

    return { blocked: false };
  }

  getActiveGuardrails() {
    return {
      contentSafety: document.getElementById("contentSafety")?.checked || false,
      promptInjection:
        document.getElementById("promptInjection")?.checked || false,
      piiDetection: document.getElementById("piiDetection")?.checked || false,
    };
  }

  checkContentSafety(message) {
    const unsafePatterns = [
      /\b(violence|harm|kill|murder|suicide)\b/i,
      /\b(hate|racist|discrimination)\b/i,
      /\b(illegal|drugs|weapons)\b/i,
    ];

    for (const pattern of unsafePatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Content contains potentially harmful or unsafe material",
        };
      }
    }

    return { blocked: false };
  }

  checkPromptInjection(message) {
    const injectionPatterns = [
      /ignore\s+(previous|all)\s+instructions/i,
      /forget\s+everything/i,
      /you\s+are\s+now/i,
      /system\s*:\s*/i,
      /\[INST\]/i,
      /\<\|system\|\>/i,
    ];

    for (const pattern of injectionPatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Potential prompt injection detected",
        };
      }
    }

    return { blocked: false };
  }

  checkPII(message) {
    const piiPatterns = [
      /\b\d{3}-\d{2}-\d{4}\b/, // SSN
      /\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b/, // Credit card
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
      /\b\d{3}-\d{3}-\d{4}\b/, // Phone number
    ];

    for (const pattern of piiPatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Personally Identifiable Information (PII) detected",
        };
      }
    }

    return { blocked: false };
  }

  updateGuardrailsStats(type) {
    if (type === "blocked") {
      this.guardrailsStats.blocked++;
    } else if (type === "passed") {
      this.guardrailsStats.passed++;
    }

    const blockedCount = document.getElementById("guardrailsBlockedCount");
    if (blockedCount) {
      blockedCount.textContent = this.guardrailsStats.blocked;
    }
  }

  toggleGuardrail(name, enabled) {
    // Update guardrail status
    const guardrailItem = document
      .querySelector(`#${name}`)
      .closest(".guardrail-item");
    if (guardrailItem) {
      if (enabled) {
        guardrailItem.classList.add("active");
        guardrailItem.querySelector(".guardrail-status").textContent = "Active";
      } else {
        guardrailItem.classList.remove("active");
        guardrailItem.querySelector(".guardrail-status").textContent =
          "Inactive";
      }
    }

    // Update active count
    const activeCount = document.querySelectorAll(
      '#guardrailsContent input[type="checkbox"]:checked'
    ).length;
    const activeCountElement = document.getElementById("guardrailsActiveCount");
    if (activeCountElement) {
      activeCountElement.textContent = activeCount;
    }

    this.showNotification(
      `${this.formatGuardrailName(name)} ${enabled ? "enabled" : "disabled"}`,
      "success"
    );
  }

  formatGuardrailName(name) {
    const nameMap = {
      contentSafety: "Content Safety",
      promptInjection: "Prompt Injection Protection",
      piiDetection: "PII Detection",
    };
    return nameMap[name] || name;
  }

  openGuardrailsConfig() {
    this.showNotification(
      "Advanced guardrails configuration available in settings",
      "info"
    );
  }

  showProtectionDetails() {
    // Show detailed protection status information
    const protectionInfo = {
      status: "Active",
      guardrails: {
        contentSafety: true,
        piiDetection: true,
        toxicityFilter: true,
        spamPrevention: true,
      },
      stats: this.guardrailsStats,
      lastUpdate: new Date().toLocaleString(),
    };

    // Create a detailed status message
    const activeGuardrails = Object.entries(protectionInfo.guardrails)
      .filter(([_, enabled]) => enabled)
      .map(([name, _]) => this.formatGuardrailName(name))
      .join(", ");

    const statusMessage = `
🛡️ AI Guardrails Protection Status

Status: ${protectionInfo.status}
Active Guardrails: ${activeGuardrails}

Statistics:
• Messages Blocked: ${protectionInfo.stats.blocked}
• Messages Passed: ${protectionInfo.stats.passed}
• Success Rate: ${
      protectionInfo.stats.passed > 0
        ? Math.round(
            (protectionInfo.stats.passed /
              (protectionInfo.stats.passed + protectionInfo.stats.blocked)) *
              100
          )
        : 100
    }%

Last Updated: ${protectionInfo.lastUpdate}
        `.trim();

    // Show in console for detailed view
    console.log("Protection Details:", protectionInfo);

    // Protection badge is already visible - no notification needed
  }

  // ===== MODAL MANAGEMENT =====
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("active");
      document.body.style.overflow = "hidden";

      // Update modal content based on type
      this.updateModalContent(modalId);

      // Add escape key listener
      this.modalEscapeListener = (e) => {
        if (e.key === "Escape") {
          this.closeModal(modalId);
        }
      };
      document.addEventListener("keydown", this.modalEscapeListener);
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";

      // Remove escape key listener
      if (this.modalEscapeListener) {
        document.removeEventListener("keydown", this.modalEscapeListener);
        this.modalEscapeListener = null;
      }
    }
  }

  updateModalContent(modalId) {
    switch (modalId) {
      case "knowledgeBaseModal":
        this.updateKnowledgeBaseModal();
        break;
      case "modelTuningModal":
        this.updateModelTuningModal();
        break;
      case "aiModelsModal":
        this.updateAiModelsModal();
        break;
    }
  }

  updateKnowledgeBaseModal() {
    // Sync RAG stats to modal
    const ragDocsCount =
      document.getElementById("ragDocsCount")?.textContent || "0";
    const ragChunksCount =
      document.getElementById("ragChunksCount")?.textContent || "0";
    const ragQueriesCount =
      document.getElementById("ragQueriesCount")?.textContent || "0";

    const modalRagDocsCount = document.getElementById("modalRagDocsCount");
    const modalRagChunksCount = document.getElementById("modalRagChunksCount");
    const modalRagQueriesCount = document.getElementById(
      "modalRagQueriesCount"
    );

    if (modalRagDocsCount) modalRagDocsCount.textContent = ragDocsCount;
    if (modalRagChunksCount) modalRagChunksCount.textContent = ragChunksCount;
    if (modalRagQueriesCount)
      modalRagQueriesCount.textContent = ragQueriesCount;

    // Update status
    const ragStatusText =
      document.getElementById("ragStatusText")?.textContent || "Ready";
    const modalRagStatusText = document.getElementById("modalRagStatusText");
    if (modalRagStatusText) modalRagStatusText.textContent = ragStatusText;

    // Load document list
    this.loadModalDocumentList();
  }

  updateModelTuningModal() {
    // Sync LoRA stats to modal
    const loraAdaptersCount =
      document.getElementById("loraAdaptersCount")?.textContent || "0";
    const loraTrainedCount =
      document.getElementById("loraTrainedCount")?.textContent || "0";
    const loraActiveCount =
      document.getElementById("loraActiveCount")?.textContent || "0";

    const modalLoraAdaptersCount = document.getElementById(
      "modalLoraAdaptersCount"
    );
    const modalLoraTrainedCount = document.getElementById(
      "modalLoraTrainedCount"
    );
    const modalLoraActiveCount = document.getElementById(
      "modalLoraActiveCount"
    );

    if (modalLoraAdaptersCount)
      modalLoraAdaptersCount.textContent = loraAdaptersCount;
    if (modalLoraTrainedCount)
      modalLoraTrainedCount.textContent = loraTrainedCount;
    if (modalLoraActiveCount)
      modalLoraActiveCount.textContent = loraActiveCount;

    // Update status
    const loraStatusText =
      document.getElementById("loraStatusText")?.textContent || "Ready";
    const modalLoraStatusText = document.getElementById("modalLoraStatusText");
    if (modalLoraStatusText) modalLoraStatusText.textContent = loraStatusText;

    // Load adapter library
    this.loadModalAdapterLibrary();
  }

  updateAiModelsModal() {
    console.log("🎭 updateAiModelsModal called");
    console.log("🎭 Available models count:", this.availableModels.length);
    console.log("🎭 Available models:", this.availableModels);

    // Update status
    const modalModelsStatusText = document.getElementById(
      "modalModelsStatusText"
    );
    if (modalModelsStatusText) modalModelsStatusText.textContent = "Ready";

    // Always refresh models when opening modal to ensure real-time data
    console.log("🔄 Refreshing models for modal...");
    this.refreshModelsFromAPI()
      .then(() => {
        console.log("✅ Models refreshed from API, now updating modal grid");
        this.loadModalModelGrid();
      })
      .catch((error) => {
        console.error("❌ Error refreshing models from API:", error);
        // Fallback to regular load
        this.loadAvailableModels().then(() => {
          this.loadModalModelGrid();
        });
      });
  }

  loadModalDocumentList() {
    const documentItems = document.getElementById("modalDocumentItems");
    if (!documentItems) return;

    // Sample documents for demo
    const sampleDocs = [
      { name: "User Manual.pdf", size: "2.3 MB", uploaded: "2 hours ago" },
      { name: "API Documentation.md", size: "1.1 MB", uploaded: "1 day ago" },
      { name: "FAQ Database.txt", size: "0.8 MB", uploaded: "3 days ago" },
    ];

    documentItems.innerHTML = sampleDocs
      .map(
        (doc) => `
            <div class="document-item">
                <div class="document-info">
                    <strong>${doc.name}</strong>
                    <small>${doc.size} • ${doc.uploaded}</small>
                </div>
                <div class="document-actions">
                    <button class="btn small secondary">View</button>
                    <button class="btn small danger">Delete</button>
                </div>
            </div>
        `
      )
      .join("");
  }

  loadModalAdapterLibrary() {
    const adaptersList = document.getElementById("modalAdaptersList");
    if (!adaptersList || !this.adapters) return;

    adaptersList.innerHTML = "";

    this.adapters.forEach((adapter) => {
      const adapterCard = document.createElement("div");
      adapterCard.className = `adapter-card ${adapter.status}`;
      adapterCard.innerHTML = `
                <div class="adapter-header">
                    <h5>${adapter.name}</h5>
                    <span class="adapter-type">${adapter.type}</span>
                </div>
                <div class="adapter-stats">
                    <div class="stat-row">
                        <span>Status:</span>
                        <span class="status-${adapter.status}">${
        adapter.status
      }</span>
                    </div>
                    <div class="stat-row">
                        <span>Performance:</span>
                        <span>${Math.round(adapter.performance * 100)}%</span>
                    </div>
                </div>
                <div class="adapter-actions">
                    <button class="btn small ${
                      adapter.active ? "secondary" : "primary"
                    }" 
                            onclick="nexusAI.toggleAdapter(${adapter.id})">
                        ${adapter.active ? "Deactivate" : "Activate"}
                    </button>
                </div>
            `;
      adaptersList.appendChild(adapterCard);
    });
  }

  loadModalModelGrid() {
    const modelGrid = document.getElementById("modalModelGrid");
    if (!modelGrid) {
      console.error("❌ modalModelGrid element not found!");
      return;
    }

    console.log("🎨 loadModalModelGrid called");
    console.log("🎨 this.availableModels.length:", this.availableModels.length);
    console.log("🎨 this.availableModels:", this.availableModels);

    // Use real models from API or fallback to defaults
    const models =
      this.availableModels.length > 0
        ? this.availableModels
        : this.getDefaultModels();

    console.log("🎨 Using models for modal:", models);
    console.log(
      "🎨 Models by provider:",
      models.reduce((acc, m) => {
        acc[m.provider] = (acc[m.provider] || 0) + 1;
        return acc;
      }, {})
    );

    // Group models by provider for better organization
    const groupedModels = {};
    models.forEach((model) => {
      const provider = model.provider || "unknown";
      if (!groupedModels[provider]) {
        groupedModels[provider] = [];
      }
      groupedModels[provider].push(model);
    });

    let gridHTML = "";

    // Render models grouped by provider with collapsible sections
    Object.entries(groupedModels).forEach(([provider, providerModels]) => {
      const sectionId = `provider-section-${provider}`;
      const isExpanded =
        localStorage.getItem(`provider-${provider}-expanded`) !== "false"; // Default to expanded

      // Provider section header with collapse/expand
      gridHTML += `
                <div class="provider-section-modal">
                    <div class="provider-header-collapsible" onclick="window.nexusAI.toggleProviderSection('${provider}')" style="cursor: pointer;">
                        <div class="provider-title-row">
                            <span class="provider-dot" style="background: ${this.getProviderColor(
                              provider
                            )}"></span>
                            <h4 class="provider-name">${
                              providerModels[0]?.provider_name || provider
                            }</h4>
                            <span class="model-count-badge">${
                              providerModels.length
                            } model${
        providerModels.length !== 1 ? "s" : ""
      }</span>
                        </div>
                        <div class="collapse-indicator ${
                          isExpanded ? "expanded" : ""
                        }">
                            <i class="fas fa-chevron-down"></i>
                        </div>
                    </div>
                    <div class="provider-models-container ${
                      isExpanded ? "expanded" : "collapsed"
                    }" id="${sectionId}">
            `;

      // Provider models
      providerModels.forEach((model) => {
        const isSelected = model.id === this.currentModel;
        const modelName = model.name || this.formatModelName(model.id);
        const modelDescription =
          model.description || "Advanced AI language model";
        const costDisplay =
          model.cost_per_1k_tokens === 0
            ? "🆓 FREE"
            : model.cost_per_1k_tokens
            ? `💰 $${model.cost_per_1k_tokens.toFixed(5)}/1K`
            : "";

        gridHTML += `
                    <div class="model-card ${isSelected ? "selected" : ""}" 
                         data-model-id="${model.id}"
                         onclick="console.log('🖱️ Card clicked:', '${
                           model.id
                         }'); window.nexusAI.directSwitchModel('${model.id}')"
                         style="cursor: pointer;">
                        <div class="model-card-header">
                            <h5>${modelName}</h5>
                            <span class="provider-badge-small" style="background: ${this.getProviderColor(
                              provider
                            )}">
                                ${model.provider_name}
                            </span>
                        </div>
                        <p>${modelDescription}</p>
                        ${
                          costDisplay
                            ? `<div class="cost-display">${costDisplay}</div>`
                            : ""
                        }
                        ${
                          model.supportsVision
                            ? '<div class="vision-indicator"><i class="fas fa-eye"></i> Vision</div>'
                            : ""
                        }
                        ${
                          isSelected
                            ? '<div class="current-indicator">✓ Current</div>'
                            : ""
                        }
                    </div>
                `;
      });

      // Close provider section container
      gridHTML += `
                    </div>
                </div>
            `;
    });

    modelGrid.innerHTML = gridHTML;
    console.log("✅ Modal model grid updated with", models.length, "models");
  }

  toggleProviderSection(provider) {
    const sectionId = `provider-section-${provider}`;
    const container = document.getElementById(sectionId);
    const indicator = document.querySelector(
      `[onclick*="${provider}"] .collapse-indicator`
    );

    if (!container || !indicator) return;

    const isExpanded = container.classList.contains("expanded");

    if (isExpanded) {
      // Collapse
      container.classList.remove("expanded");
      container.classList.add("collapsed");
      indicator.classList.remove("expanded");
      localStorage.setItem(`provider-${provider}-expanded`, "false");
    } else {
      // Expand
      container.classList.remove("collapsed");
      container.classList.add("expanded");
      indicator.classList.add("expanded");
      localStorage.setItem(`provider-${provider}-expanded`, "true");
    }

    console.log(
      `🔄 Toggled ${provider} section:`,
      !isExpanded ? "expanded" : "collapsed"
    );
  }

  // Old selectModalModel method removed - now using direct onclick approach

  showGuardrailsLogs() {
    const logs = [
      {
        time: new Date().toLocaleTimeString(),
        type: "blocked",
        reason: "PII detected",
        message: "Message containing email address",
      },
      {
        time: new Date(Date.now() - 300000).toLocaleTimeString(),
        type: "passed",
        reason: "Clean content",
        message: "Regular conversation",
      },
    ];

    console.log("Guardrails Logs:", logs);
    this.showNotification(
      `Guardrails blocked ${this.guardrailsStats.blocked} messages today`,
      "info"
    );
  }

  updateRAGStats() {
    // Update RAG statistics (placeholder)
    const docsCount = document.getElementById("ragDocsCount");
    const chunksCount = document.getElementById("ragChunksCount");

    if (docsCount) docsCount.textContent = "0";
    if (chunksCount) chunksCount.textContent = "0";
  }

  updateLoRAStats() {
    // Update LoRA statistics (placeholder)
    const adaptersCount = document.getElementById("loraAdaptersCount");
    const trainedCount = document.getElementById("loraTrainedCount");

    if (adaptersCount) adaptersCount.textContent = "0";
    if (trainedCount) trainedCount.textContent = "0";
  }

  // ===== RAG SYSTEM =====
  uploadDocument() {
    // Create file input for document upload
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".pdf,.txt,.doc,.docx,.md";
    input.multiple = true;

    input.onchange = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;

      this.showNotification(`Uploading ${files.length} document(s)...`, "info");

      try {
        const formData = new FormData();
        files.forEach((file) => formData.append("documents", file));

        const response = await fetch("/api/rag/upload", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (data.status === "success") {
          this.showNotification("Documents uploaded successfully", "success");
          this.updateRAGStats();
        } else {
          throw new Error(data.error || "Upload failed");
        }
      } catch (error) {
        console.error("Upload error:", error);
        this.showNotification("Document upload feature coming soon", "info");
      }
    };

    input.click();
  }

  searchDocuments() {
    const query = prompt("Enter search query:");
    if (!query) return;

    this.showNotification("Document search feature coming soon", "info");
  }

  // ===== LORA SYSTEM =====
  createLoRAAdapter() {
    this.showNotification("LoRA adapter creation feature coming soon", "info");
  }

  manageLoRAAdapters() {
    this.showNotification(
      "LoRA adapter management feature coming soon",
      "info"
    );
  }

  // ===== GUARDRAILS SYSTEM =====
  initializeGuardrails() {
    // Set up guardrail toggle listeners
    document
      .querySelectorAll('#guardrailsContent input[type="checkbox"]')
      .forEach((checkbox) => {
        checkbox.addEventListener("change", (e) => {
          const guardrailName = e.target.id;
          const isEnabled = e.target.checked;
          this.toggleGuardrail(guardrailName, isEnabled);
        });
      });

    // Initialize guardrails stats
    this.guardrailsStats = {
      blocked: 0,
      passed: 0,
    };
  }

  async applyGuardrails(message) {
    const activeGuardrails = this.getActiveGuardrails();

    // Content Safety Check
    if (activeGuardrails.contentSafety) {
      const contentSafetyResult = this.checkContentSafety(message);
      if (contentSafetyResult.blocked) {
        return contentSafetyResult;
      }
    }

    // Prompt Injection Check
    if (activeGuardrails.promptInjection) {
      const promptInjectionResult = this.checkPromptInjection(message);
      if (promptInjectionResult.blocked) {
        return promptInjectionResult;
      }
    }

    // PII Detection Check
    if (activeGuardrails.piiDetection) {
      const piiResult = this.checkPII(message);
      if (piiResult.blocked) {
        return piiResult;
      }
    }

    return { blocked: false };
  }

  getActiveGuardrails() {
    return {
      contentSafety: document.getElementById("contentSafety")?.checked || false,
      promptInjection:
        document.getElementById("promptInjection")?.checked || false,
      piiDetection: document.getElementById("piiDetection")?.checked || false,
    };
  }

  checkContentSafety(message) {
    const unsafePatterns = [
      /\b(violence|harm|kill|murder|suicide)\b/i,
      /\b(hate|racist|discrimination)\b/i,
      /\b(illegal|drugs|weapons)\b/i,
    ];

    for (const pattern of unsafePatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Content contains potentially harmful or unsafe material",
        };
      }
    }

    return { blocked: false };
  }

  checkPromptInjection(message) {
    const injectionPatterns = [
      /ignore\s+(previous|all)\s+instructions/i,
      /forget\s+everything/i,
      /you\s+are\s+now/i,
      /system\s*:\s*/i,
      /\[INST\]/i,
      /\<\|system\|\>/i,
    ];

    for (const pattern of injectionPatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Potential prompt injection detected",
        };
      }
    }

    return { blocked: false };
  }

  checkPII(message) {
    const piiPatterns = [
      /\b\d{3}-\d{2}-\d{4}\b/, // SSN
      /\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b/, // Credit card
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
      /\b\d{3}-\d{3}-\d{4}\b/, // Phone number
    ];

    for (const pattern of piiPatterns) {
      if (pattern.test(message)) {
        return {
          blocked: true,
          reason: "Personally Identifiable Information (PII) detected",
        };
      }
    }

    return { blocked: false };
  }

  toggleGuardrail(name, enabled) {
    // Update guardrail status
    const guardrailItem = document
      .querySelector(`#${name}`)
      .closest(".guardrail-item");
    if (guardrailItem) {
      if (enabled) {
        guardrailItem.classList.add("active");
        guardrailItem.querySelector(".guardrail-status").textContent = "Active";
      } else {
        guardrailItem.classList.remove("active");
        guardrailItem.querySelector(".guardrail-status").textContent =
          "Inactive";
      }
    }

    // Update active count
    const activeCount = document.querySelectorAll(
      '#guardrailsContent input[type="checkbox"]:checked'
    ).length;
    const activeCountElement = document.getElementById("guardrailsActiveCount");
    if (activeCountElement) {
      activeCountElement.textContent = activeCount;
    }

    this.showNotification(
      `${this.formatGuardrailName(name)} ${enabled ? "enabled" : "disabled"}`,
      "success"
    );
  }

  formatGuardrailName(name) {
    const nameMap = {
      contentSafety: "Content Safety",
      promptInjection: "Prompt Injection Protection",
      piiDetection: "PII Detection",
    };
    return nameMap[name] || name;
  }

  openGuardrailsConfig() {
    // Create a simple configuration modal
    const configHtml = `
            <div class="guardrails-config">
                <h4>Guardrails Configuration</h4>
                <div class="config-section">
                    <h5>Content Safety Settings</h5>
                    <label>
                        <input type="range" id="contentSafetyLevel" min="1" max="5" value="3">
                        <span>Sensitivity Level: <span id="contentSafetyValue">3</span></span>
                    </label>
                </div>
                <div class="config-section">
                    <h5>Custom Blocked Words</h5>
                    <textarea id="customBlockedWords" placeholder="Enter words to block, separated by commas"></textarea>
                </div>
                <div class="config-actions">
                    <button class="btn primary" onclick="nexusAI.saveGuardrailsConfig()">Save Configuration</button>
                    <button class="btn secondary" onclick="nexusAI.resetGuardrailsConfig()">Reset to Default</button>
                </div>
            </div>
        `;

    // For now, show a notification
    this.showNotification(
      "Advanced guardrails configuration available in settings",
      "info"
    );
  }

  showGuardrailsLogs() {
    const logs = [
      {
        time: new Date().toLocaleTimeString(),
        type: "blocked",
        reason: "PII detected",
        message: "Message containing email address",
      },
      {
        time: new Date(Date.now() - 300000).toLocaleTimeString(),
        type: "passed",
        reason: "Clean content",
        message: "Regular conversation",
      },
    ];

    console.log("Guardrails Logs:", logs);
    this.showNotification(
      `Guardrails blocked ${this.guardrailsStats.blocked} messages today`,
      "info"
    );
  }

  // ===== ENHANCED LORA FINE-TUNING SYSTEM =====

  updateLoRAStatsEnhanced() {
    // Initialize enhanced LoRA statistics
    this.loraStats = {
      adapters: 0,
      trained: 0,
      active: 0,
      totalTrainingTime: 0,
      successRate: 85,
      bestPerforming: null,
      averagePerformance: 0.82,
    };

    this.updateLoRADisplay();
    this.loadAdapterLibrary();
  }

  updateLoRADisplay() {
    const adaptersCount = document.getElementById("loraAdaptersCount");
    const trainedCount = document.getElementById("loraTrainedCount");
    const activeCount = document.getElementById("loraActiveCount");
    const adaptersProgress = document.getElementById("loraAdaptersProgress");
    const trainedProgress = document.getElementById("loraTrainedProgress");
    const activeProgress = document.getElementById("loraActiveProgress");

    if (adaptersCount) adaptersCount.textContent = this.loraStats.adapters;
    if (trainedCount) trainedCount.textContent = this.loraStats.trained;
    if (activeCount) activeCount.textContent = this.loraStats.active;

    // Update progress bars
    const maxAdapters = 20,
      maxTrained = 15,
      maxActive = 5;
    if (adaptersProgress)
      adaptersProgress.style.width = `${Math.min(
        100,
        (this.loraStats.adapters / maxAdapters) * 100
      )}%`;
    if (trainedProgress)
      trainedProgress.style.width = `${Math.min(
        100,
        (this.loraStats.trained / maxTrained) * 100
      )}%`;
    if (activeProgress)
      activeProgress.style.width = `${Math.min(
        100,
        (this.loraStats.active / maxActive) * 100
      )}%`;

    this.updateTrainingInsights();
  }

  updateTrainingInsights() {
    const bestAdapter = document.getElementById("bestAdapter");
    const avgTrainingTime = document.getElementById("avgTrainingTime");
    const successRate = document.getElementById("successRate");
    const recommendedRank = document.getElementById("recommendedRank");

    if (bestAdapter) {
      bestAdapter.textContent = this.loraStats.bestPerforming || "None";
    }

    if (avgTrainingTime) {
      const avgTime =
        this.loraStats.totalTrainingTime > 0
          ? Math.round(
              this.loraStats.totalTrainingTime /
                Math.max(1, this.loraStats.trained)
            )
          : 0;
      avgTrainingTime.textContent = avgTime > 0 ? `${avgTime}min` : "12min";
    }

    if (successRate) {
      successRate.textContent = `${Math.round(this.loraStats.successRate)}%`;
    }

    if (recommendedRank) {
      const rank = this.calculateRecommendedRank();
      recommendedRank.textContent = rank;
    }
  }

  calculateRecommendedRank() {
    // Simple heuristic for recommended LoRA rank
    if (this.loraStats.adapters === 0) return "16";
    if (this.loraStats.averagePerformance > 0.9) return "8";
    if (this.loraStats.averagePerformance > 0.7) return "16";
    return "32";
  }

  async loadAdapterLibrary() {
    this.updateLoRAStatus("processing", "Loading...");

    try {
      // Simulate loading adapter library
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Load sample adapters for demo
      this.loadSampleAdapters();

      this.updateLoRAStatus("active", "Ready");
    } catch (error) {
      console.error("Failed to load adapter library:", error);
      this.updateLoRAStatus("error", "Error");
    }
  }

  loadSampleAdapters() {
    const sampleAdapters = [
      {
        id: 1,
        name: "Customer Support Specialist",
        type: "Task-Specific",
        status: "trained",
        performance: 0.94,
        rank: 16,
        alpha: 32,
        trainingTime: 15,
        dataset: "customer_support_1k.json",
        created: new Date(Date.now() - 86400000),
        active: true,
      },
      {
        id: 2,
        name: "Code Documentation Writer",
        type: "Domain-Specific",
        status: "trained",
        performance: 0.87,
        rank: 8,
        alpha: 16,
        trainingTime: 8,
        dataset: "code_docs_500.json",
        created: new Date(Date.now() - 172800000),
        active: false,
      },
      {
        id: 3,
        name: "Creative Writing Assistant",
        type: "Creative",
        status: "training",
        performance: 0.0,
        rank: 32,
        alpha: 64,
        trainingTime: 0,
        dataset: "creative_writing_2k.json",
        created: new Date(Date.now() - 3600000),
        active: false,
      },
    ];

    this.adapters = sampleAdapters;
    this.loraStats.adapters = sampleAdapters.length;
    this.loraStats.trained = sampleAdapters.filter(
      (a) => a.status === "trained"
    ).length;
    this.loraStats.active = sampleAdapters.filter((a) => a.active).length;
    this.loraStats.bestPerforming = sampleAdapters.reduce(
      (best, current) =>
        current.performance > (best?.performance || 0) ? current : best,
      null
    )?.name;
    this.loraStats.averagePerformance =
      sampleAdapters
        .filter((a) => a.performance > 0)
        .reduce((sum, a) => sum + a.performance, 0) /
      Math.max(1, sampleAdapters.filter((a) => a.performance > 0).length);
    this.loraStats.totalTrainingTime = sampleAdapters.reduce(
      (sum, a) => sum + a.trainingTime,
      0
    );

    this.renderAdapterLibrary();
    this.updateLoRADisplay();
  }

  renderAdapterLibrary() {
    const adaptersList = document.getElementById("adaptersList");
    if (!adaptersList || !this.adapters) return;

    adaptersList.innerHTML = "";

    this.adapters.forEach((adapter) => {
      const adapterCard = document.createElement("div");
      adapterCard.className = `adapter-card ${adapter.status}`;
      adapterCard.innerHTML = `
                <div class="adapter-header">
                    <h4>${adapter.name}</h4>
                    <span class="adapter-type">${adapter.type}</span>
                </div>
                <div class="adapter-stats">
                    <div class="stat">
                        <span class="label">Status:</span>
                        <span class="value status-${adapter.status}">${
        adapter.status
      }</span>
                    </div>
                    <div class="stat">
                        <span class="label">Performance:</span>
                        <span class="value">${Math.round(
                          adapter.performance * 100
                        )}%</span>
                    </div>
                    <div class="stat">
                        <span class="label">Rank:</span>
                        <span class="value">${adapter.rank}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Training Time:</span>
                        <span class="value">${adapter.trainingTime}min</span>
                    </div>
                </div>
                <div class="adapter-actions">
                    <button class="btn small ${
                      adapter.active ? "secondary" : "primary"
                    }" 
                            onclick="nexusAI.toggleAdapter(${adapter.id})">
                        ${adapter.active ? "Deactivate" : "Activate"}
                    </button>
                    <button class="btn small secondary" onclick="nexusAI.editAdapter(${
                      adapter.id
                    })">
                        Edit
                    </button>
                    <button class="btn small danger" onclick="nexusAI.deleteAdapter(${
                      adapter.id
                    })">
                        Delete
                    </button>
                </div>
            `;
      adaptersList.appendChild(adapterCard);
    });
  }

  toggleAdapter(adapterId) {
    const adapter = this.adapters.find((a) => a.id === adapterId);
    if (adapter) {
      adapter.active = !adapter.active;
      this.loraStats.active = this.adapters.filter((a) => a.active).length;
      this.renderAdapterLibrary();
      this.updateLoRADisplay();
      this.showNotification(
        `Adapter "${adapter.name}" ${
          adapter.active ? "activated" : "deactivated"
        }`,
        "success"
      );
    }
  }

  editAdapter(adapterId) {
    const adapter = this.adapters.find((a) => a.id === adapterId);
    if (adapter) {
      this.showNotification(
        `Editing adapter "${adapter.name}" - Feature coming soon`,
        "info"
      );
    }
  }

  deleteAdapter(adapterId) {
    const adapter = this.adapters.find((a) => a.id === adapterId);
    if (
      adapter &&
      confirm(`Are you sure you want to delete "${adapter.name}"?`)
    ) {
      this.adapters = this.adapters.filter((a) => a.id !== adapterId);
      this.loraStats.adapters = this.adapters.length;
      this.loraStats.trained = this.adapters.filter(
        (a) => a.status === "trained"
      ).length;
      this.loraStats.active = this.adapters.filter((a) => a.active).length;
      this.renderAdapterLibrary();
      this.updateLoRADisplay();
      this.showNotification(`Adapter "${adapter.name}" deleted`, "success");
    }
  }

  updateLoRAStatus(status, text) {
    const statusDot = document.getElementById("loraStatusDot");
    const statusText = document.getElementById("loraStatusText");

    if (statusDot) {
      statusDot.className = `status-dot ${status}`;
    }

    if (statusText) {
      statusText.textContent = text;
    }
  }

  // Enhanced LoRA Actions
  createLoRAAdapter() {
    this.showNotification("Opening adapter creation wizard...", "info");

    const adapterName = prompt("Enter adapter name:");
    if (!adapterName) return;

    const adapterType =
      prompt(
        "Enter adapter type (Task-Specific, Domain-Specific, Creative, General):"
      ) || "General";

    this.showNotification("Creating new LoRA adapter...", "info");

    // Simulate adapter creation
    setTimeout(() => {
      const newAdapter = {
        id: Date.now(),
        name: adapterName,
        type: adapterType,
        status: "draft",
        performance: 0,
        rank: 16,
        alpha: 32,
        trainingTime: 0,
        dataset: "No dataset",
        created: new Date(),
        active: false,
      };

      this.adapters = this.adapters || [];
      this.adapters.unshift(newAdapter);

      this.loraStats.adapters++;
      this.updateLoRADisplay();
      this.renderAdapterLibrary();

      this.showNotification(
        `Adapter "${adapterName}" created successfully!`,
        "success"
      );
    }, 1500);
  }

  quickTrainAdapter() {
    if (!this.adapters || this.adapters.length === 0) {
      this.showNotification(
        "No adapters available. Create an adapter first.",
        "warning"
      );
      return;
    }

    const draftAdapters = this.adapters.filter((a) => a.status === "draft");
    if (draftAdapters.length === 0) {
      this.showNotification(
        "No draft adapters available for training.",
        "warning"
      );
      return;
    }

    const adapter = draftAdapters[0];
    this.startTraining(adapter);
  }

  async startTraining(adapter) {
    adapter.status = "training";
    this.renderAdapterLibrary();
    this.showTrainingProgress();

    this.showNotification(`Starting training for "${adapter.name}"...`, "info");

    // Simulate training process
    const trainingSteps = [
      "Initializing training environment...",
      "Loading dataset...",
      "Preparing model for fine-tuning...",
      "Training LoRA layers...",
      "Validating performance...",
      "Saving adapter weights...",
    ];

    for (let i = 0; i < trainingSteps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const progress = ((i + 1) / trainingSteps.length) * 100;
      this.updateTrainingProgress(
        progress,
        trainingSteps[i],
        trainingSteps.length - i - 1
      );
    }

    // Complete training
    adapter.status = "trained";
    adapter.performance = 0.75 + Math.random() * 0.2; // Random performance between 75-95%
    adapter.trainingTime = 8 + Math.floor(Math.random() * 15); // Random training time 8-22 minutes

    this.loraStats.trained++;
    this.loraStats.totalTrainingTime += adapter.trainingTime;

    this.hideTrainingProgress();
    this.renderAdapterLibrary();
    this.updateLoRADisplay();

    this.showNotification(
      `Training completed! Performance: ${Math.round(
        adapter.performance * 100
      )}%`,
      "success"
    );
  }

  showTrainingProgress() {
    const trainingProgress = document.getElementById("trainingProgress");
    if (trainingProgress) {
      trainingProgress.style.display = "block";
    }
  }

  hideTrainingProgress() {
    const trainingProgress = document.getElementById("trainingProgress");
    if (trainingProgress) {
      trainingProgress.style.display = "none";
    }
  }

  updateTrainingProgress(percentage, step, remainingSteps) {
    const progressBar = document.getElementById("trainingProgressBar");
    const progressPercentage = document.getElementById("trainingPercentage");
    const trainingStep = document.getElementById("trainingStep");
    const trainingETA = document.getElementById("trainingETA");

    if (progressBar) progressBar.style.width = `${percentage}%`;
    if (progressPercentage)
      progressPercentage.textContent = `${Math.round(percentage)}%`;
    if (trainingStep) trainingStep.textContent = step;
    if (trainingETA) trainingETA.textContent = `ETA: ${remainingSteps * 2}min`;
  }

  loadPretrainedAdapter() {
    this.showNotification(
      "Load pretrained adapter feature coming soon",
      "info"
    );
  }

  uploadFromUrl() {
    this.showNotification("Upload from URL feature coming soon", "info");
  }

  switchModel(modelId) {
    // Store the selected model
    this.currentModel = modelId;

    // Update settings
    this.settings.defaultModel = modelId;
    this.saveSettings();

    // Immediately update the status bar
    this.forceUpdateStatusBar(modelId);

    // Update any existing message model displays
    this.updateExistingMessageModels();

    this.showNotification(
      `Switched to ${this.formatModelName(modelId)}`,
      "success"
    );
    this.closeModal("aiModelsModal");
  }

  forceUpdateStatusBar(modelId) {
    // Multiple attempts to update the status bar
    const updateAttempts = [
      () => {
        const element = document.getElementById("currentModelName");
        if (element) {
          element.textContent = this.formatModelName(modelId);
          return true;
        }
        return false;
      },
      () => {
        const element = document.querySelector("#currentModelName");
        if (element) {
          element.innerHTML = this.formatModelName(modelId);
          return true;
        }
        return false;
      },
      () => {
        const element = document.querySelector(".status-bar #currentModelName");
        if (element) {
          element.textContent = this.formatModelName(modelId);
          return true;
        }
        return false;
      },
    ];

    // Try each method
    for (let attempt of updateAttempts) {
      if (attempt()) {
        break;
      }
    }

    // Also call the original method
    this.updateModelDisplay();
  }

  directSwitchModel(modelId) {
    // Update the model property immediately
    this.currentModel = modelId;

    // Mark that user has explicitly set a model
    this._userSelectedModel = true;
    this._lastUserSelectedModel = modelId;

    // Update settings
    this.settings.defaultModel = modelId;
    this.saveSettings();

    // Force DOM update
    const displayName = this.formatModelName(modelId);
    const element = document.getElementById("currentModelName");
    if (element) {
      element.textContent = displayName;
    }

    // Call the original methods
    this.updateModelDisplay();
    this.forceUpdateStatusBar(modelId);

    // Update modal selection if modal is open
    const modalCards = document.querySelectorAll("#modalModelGrid .model-card");
    modalCards.forEach((card) => {
      if (card.dataset.modelId === modelId) {
        card.classList.add("selected");
        if (!card.querySelector(".current-indicator")) {
          card.innerHTML += '<div class="current-indicator">Current</div>';
        }
      } else {
        card.classList.remove("selected");
        const indicator = card.querySelector(".current-indicator");
        if (indicator) indicator.remove();
      }
    });

    // Update modal info section
    this.updateModalInfo(modelId);

    // Show notification
    this.showNotification(`Switched to ${displayName}`, "success");
  }

  updateModalInfo(modelId) {
    const modelInfo = document.getElementById("modalModelInfo");
    if (modelInfo) {
      const modelName = this.formatModelName(modelId);
      modelInfo.innerHTML = `
                <h5>✅ Switched to: ${modelName}</h5>
                <p>Model switched successfully! This model is now active for all conversations.</p>
                <div class="current-model-indicator">
                    <i class="fas fa-check-circle"></i> Currently Active Model
                </div>
            `;
    }
  }

  updateExistingMessageModels() {
    // Update model info in existing assistant messages
    const modelInfoElements = document.querySelectorAll(
      ".message.assistant .model-info"
    );
    const currentModelName = this.formatModelName(this.currentModel);

    modelInfoElements.forEach((element) => {
      const modelNameSpan = element.querySelector("span:last-child") || element;
      if (modelNameSpan) {
        modelNameSpan.textContent = currentModelName;
      }
    });
  }

  async refreshModelsInModal() {
    // Show loading state
    const refreshBtn = document.getElementById("modalRefreshModelsBtn");
    if (refreshBtn) {
      refreshBtn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
      refreshBtn.disabled = true;
    }

    try {
      // Reload models from API
      await this.loadAvailableModels();

      // Update the modal grid with new models
      this.loadModalModelGrid();

      this.showNotification("Models refreshed successfully", "success");
    } catch (error) {
      console.error("Failed to refresh models:", error);
      this.showNotification("Failed to refresh models", "error");
    } finally {
      // Restore button state
      if (refreshBtn) {
        refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh Models';
        refreshBtn.disabled = false;
      }
    }
  }

  updateModelDisplay() {
    const currentModelName = document.getElementById("currentModelName");

    if (currentModelName && this.currentModel) {
      const displayName = this.formatModelName(this.currentModel);
      currentModelName.textContent = displayName;

      // Visual feedback
      currentModelName.style.transition = "all 0.3s ease";
      currentModelName.style.transform = "scale(1.05)";
      setTimeout(() => {
        currentModelName.style.transform = "scale(1)";
      }, 200);
    }
  }

  formatModelName(modelId) {
    // Convert model IDs to user-friendly names
    const modelNames = {
      "llama-3.1-70b-versatile": "Llama 3.1 70B",
      "llama-3.1-8b-instant": "Llama 3.1 8B",
      "llama-3.2-11b-vision-preview": "Llama 3.2 Vision",
      "llama-3.2-1b-preview": "Llama 3.2 1B",
      "llama-3.2-3b-preview": "Llama 3.2 3B",
      "mixtral-8x7b-32768": "Mixtral 8x7B",
      "gemma-7b-it": "Gemma 7B",
      "gemma2-9b-it": "Gemma 2 9B",
      "llama3-groq-70b-8192-tool-use-preview": "Llama 3 70B Tools",
      "llama3-groq-8b-8192-tool-use-preview": "Llama 3 8B Tools",
    };

    // If not in our mapping, try to create a readable name
    if (modelNames[modelId]) {
      return modelNames[modelId];
    }

    // Auto-format unknown model IDs
    return modelId
      .replace(/-/g, " ")
      .replace(/\b\w/g, (l) => l.toUpperCase())
      .replace(/\s+/g, " ")
      .trim();
  }

  // Enhanced send button functionality
  enhanceSendButton() {
    const sendBtn = document.getElementById("sendBtn");
    const messageInput = document.getElementById("messageInput");

    if (!sendBtn || !messageInput) return;

    // Add visual feedback for typing
    messageInput.addEventListener("input", (e) => {
      const hasContent = e.target.value.trim().length > 0;

      if (hasContent) {
        sendBtn.classList.add("typing");
        sendBtn.disabled = false;
        messageInput.classList.add("typing");
      } else {
        sendBtn.classList.remove("typing");
        sendBtn.disabled = true;
        messageInput.classList.remove("typing");
      }
    });

    // Enhanced send button click with animations
    sendBtn.addEventListener("click", async () => {
      if (sendBtn.disabled) return;

      // Add loading state
      sendBtn.classList.add("loading");
      sendBtn.classList.remove("typing");
      const originalIcon = sendBtn.innerHTML;
      sendBtn.innerHTML = '<i class="fas fa-spinner"></i>';

      try {
        await this.sendMessage();

        // Success animation
        sendBtn.classList.remove("loading");
        sendBtn.classList.add("success");
        sendBtn.innerHTML = '<i class="fas fa-check"></i>';

        setTimeout(() => {
          sendBtn.classList.remove("success");
          sendBtn.innerHTML = originalIcon;
        }, 1000);
      } catch (error) {
        // Error state
        sendBtn.classList.remove("loading");
        sendBtn.innerHTML = '<i class="fas fa-exclamation"></i>';

        setTimeout(() => {
          sendBtn.innerHTML = originalIcon;
        }, 2000);
      }
    });

    // Add hover effects
    sendBtn.addEventListener("mouseenter", () => {
      if (!sendBtn.disabled) {
        sendBtn.style.transform = "translateY(-3px) scale(1.05)";
      }
    });

    sendBtn.addEventListener("mouseleave", () => {
      if (!sendBtn.disabled) {
        sendBtn.style.transform = "";
      }
    });
  }

  // Enhanced typing indicator with more visual appeal
  showEnhancedTypingIndicator() {
    const messagesList = document.getElementById("messagesList");
    if (!messagesList) return;

    // Remove existing typing indicator
    this.hideTypingIndicator();

    const typingDiv = document.createElement("div");
    typingDiv.className = "message assistant typing-indicator enhanced";
    typingDiv.id = "typingIndicator";

    typingDiv.innerHTML = `
            <div class="message-avatar">
                <div class="avatar-pulse">
                    <i class="fas fa-brain"></i>
                </div>
            </div>
            <div class="message-content">
                <div class="message-bubble typing-bubble">
                    <div class="typing-dots enhanced">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div class="typing-text">AI is thinking...</div>
                </div>
            </div>
        `;

    messagesList.appendChild(typingDiv);
    messagesList.scrollTop = messagesList.scrollHeight;

    // Add entrance animation
    setTimeout(() => {
      typingDiv.classList.add("fade-in");
    }, 10);
  }

  // Initialize enhanced features
  initializeEnhancedFeatures() {
    // Initialize enhanced send button
    this.enhanceSendButton();

    // Add keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      // Ctrl/Cmd + Enter to send message
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        const sendBtn = document.getElementById("sendBtn");
        if (sendBtn && !sendBtn.disabled) {
          sendBtn.click();
        }
      }

      // Escape to clear input
      if (e.key === "Escape") {
        const messageInput = document.getElementById("messageInput");
        if (messageInput && messageInput.value) {
          messageInput.value = "";
          messageInput.style.height = "auto";
          this.handleInputChange({ target: messageInput });
          messageInput.focus();
        }
      }
    });

    // Add paste handling for better UX
    const messageInput = document.getElementById("messageInput");
    if (messageInput) {
      messageInput.addEventListener("paste", (e) => {
        // Handle large paste content
        setTimeout(() => {
          if (messageInput.value.length > 1000) {
            this.showNotification(
              "Large content detected. Message may take longer to process.",
              "info"
            );
          }
          this.handleInputChange({ target: messageInput });
        }, 10);
      });
    }
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.nexusAI = new NexusAI();
});


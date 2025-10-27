/**
 * NexusAI Modular Application
 * ===========================
 * Main application class using modular architecture
 */

import ModuleLoader from './core/moduleLoader.js';

class NexusAIModular {
    constructor() {
        this.conversations = [];
        this.currentConversation = null;
        this.settings = this.loadSettings();
        this.currentModel = this.settings.defaultModel || "llama-3.1-8b-instant";
        this.availableModels = [];
        
        // Initialize guardrails stats
        this.guardrailsStats = {
            blocked: 0,
            passed: 0,
        };

        // Module loader
        this.moduleLoader = new ModuleLoader();
        
        this.init();
    }

    async init() {
        console.log("🚀 Initializing NexusAI Modular...");
        
        try {
            // Register modules
            this.registerModules();
            
            // Load core modules first
            await this.loadCoreModules();
            
            // Setup basic event listeners
            this.setupBasicEventListeners();
            
            // Load settings and conversations
            this.loadConversations();
            this.applySettings();
            
            // Initialize UI
            this.initializeUI();
            
            console.log("✅ NexusAI Modular initialized successfully");
            
        } catch (error) {
            console.error("❌ Failed to initialize NexusAI Modular:", error);
            // Fallback to basic functionality
            this.initializeFallback();
        }
    }

    registerModules() {
        // Register all available modules
        this.moduleLoader.register('chat', '../modules/chat.js', []);
        this.moduleLoader.register('models', '../modules/models.js', []);
        // Future modules will be registered here:
        // this.moduleLoader.register('rag', '../modules/rag.js', []);
        // this.moduleLoader.register('lora', '../modules/lora.js', []);
    }

    async loadCoreModules() {
        // Load essential modules
        await this.moduleLoader.load('chat', this);
        await this.moduleLoader.load('models', this);
    }

    setupBasicEventListeners() {
        // Header controls
        document.getElementById("sidebarToggle")?.addEventListener("click", () => this.toggleSidebar());
        document.getElementById("newChatBtn")?.addEventListener("click", () => this.startNewChat());
        document.getElementById("settingsBtn")?.addEventListener("click", () => this.openSettings());
        document.getElementById("clearAllBtn")?.addEventListener("click", () => this.clearAllConversations());
        document.getElementById("exportBtn")?.addEventListener("click", () => this.exportConversations());

        // Panel toggles
        document.querySelectorAll(".panel-toggle").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const panel = e.currentTarget.dataset.panel;
                this.togglePanel(panel);
            });
        });

        // Modal controls
        document.querySelectorAll(".modal-close").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const modalId = e.target.closest(".modal-close").dataset.modal;
                this.closeModal(modalId);
            });
        });

        // Keyboard shortcuts
        document.addEventListener("keydown", (e) => {
            // Ctrl/Cmd + N for new chat
            if ((e.ctrlKey || e.metaKey) && e.key === "n") {
                e.preventDefault();
                this.startNewChat();
            }
            // Escape to close modals
            if (e.key === "Escape") {
                this.closeAllModals();
            }
        });
    }

    initializeUI() {
        // Show welcome screen initially
        const chatModule = this.moduleLoader.get('chat');
        if (chatModule) {
            chatModule.showWelcomeScreen();
        }
        
        // Update model display
        setTimeout(() => {
            this.updateModelDisplay();
        }, 500);
    }

    initializeFallback() {
        console.log("🔄 Initializing fallback mode...");
        // Basic functionality without modules
        this.setupBasicEventListeners();
        this.loadConversations();
        this.applySettings();
    }

    // ===== CONVERSATION MANAGEMENT =====
    
    startNewChat() {
        const chatModule = this.moduleLoader.get('chat');
        if (chatModule) {
            chatModule.clearChat();
        }
        
        this.currentConversation = {
            id: Date.now().toString(),
            title: "New Chat",
            messages: [],
            createdAt: new Date(),
            model: this.currentModel
        };
        
        this.conversations.unshift(this.currentConversation);
        this.saveConversations();
        this.renderConversations();
        
        this.showNotification("New chat started", "success");
    }

    loadConversations() {
        try {
            const saved = localStorage.getItem("nexusai_conversations");
            if (saved) {
                this.conversations = JSON.parse(saved);
                // Convert date strings back to Date objects
                this.conversations.forEach(conv => {
                    conv.createdAt = new Date(conv.createdAt);
                    conv.messages.forEach(msg => {
                        msg.timestamp = new Date(msg.timestamp);
                    });
                });
            }
            this.renderConversations();
        } catch (error) {
            console.error("Error loading conversations:", error);
            this.conversations = [];
        }
    }

    saveConversations() {
        try {
            localStorage.setItem("nexusai_conversations", JSON.stringify(this.conversations));
        } catch (error) {
            console.error("Error saving conversations:", error);
        }
    }

    renderConversations() {
        const conversationsList = document.getElementById("conversationsList");
        if (!conversationsList) return;

        conversationsList.innerHTML = "";

        this.conversations.forEach((conversation) => {
            const item = document.createElement("div");
            item.className = "conversation-item";
            if (this.currentConversation && conversation.id === this.currentConversation.id) {
                item.classList.add("active");
            }

            const lastMessage = conversation.messages[conversation.messages.length - 1];
            const preview = lastMessage 
                ? lastMessage.content.substring(0, 50) + "..."
                : "New conversation";

            item.innerHTML = `
                <div class="conversation-info">
                    <div class="conversation-title">${conversation.title}</div>
                    <div class="conversation-preview">${preview}</div>
                    <div class="conversation-meta">
                        <span class="conversation-date">${conversation.createdAt.toLocaleDateString()}</span>
                        <span class="conversation-model">${this.formatModelName(conversation.model)}</span>
                    </div>
                </div>
                <div class="conversation-actions">
                    <button class="action-btn delete" title="Delete conversation">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

            item.addEventListener("click", () => this.loadConversation(conversation.id));

            // Add delete handler
            const deleteBtn = item.querySelector(".delete");
            deleteBtn?.addEventListener("click", (e) => {
                e.stopPropagation();
                this.deleteConversation(conversation.id);
            });

            conversationsList.appendChild(item);
        });
    }

    // ===== SETTINGS MANAGEMENT =====
    
    loadSettings() {
        try {
            const saved = localStorage.getItem("nexusai_settings");
            return saved ? JSON.parse(saved) : {
                theme: 'auto',
                defaultModel: 'llama-3.1-8b-instant',
                autoSave: true,
                compactMode: false
            };
        } catch (error) {
            console.error("Error loading settings:", error);
            return {
                theme: 'auto',
                defaultModel: 'llama-3.1-8b-instant',
                autoSave: true,
                compactMode: false
            };
        }
    }

    saveSettings() {
        try {
            localStorage.setItem("nexusai_settings", JSON.stringify(this.settings));
        } catch (error) {
            console.error("Error saving settings:", error);
        }
    }

    applySettings() {
        // Apply theme
        this.applyTheme();
        
        // Apply other settings
        if (this.settings.compactMode) {
            document.body.classList.add('compact-mode');
        } else {
            document.body.classList.remove('compact-mode');
        }
    }

    applyTheme() {
        const theme = this.settings.theme || 'auto';
        
        if (theme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
    }

    // ===== UI HELPERS =====
    
    toggleSidebar() {
        const sidebar = document.getElementById("sidebar");
        sidebar?.classList.toggle("open");
    }

    togglePanel(panelName) {
        const panel = document.querySelector(`[data-panel="${panelName}"]`);
        const content = document.getElementById(`${panelName}Content`);
        
        if (panel && content) {
            panel.classList.toggle("expanded");
            content.classList.toggle("expanded");
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal?.classList.remove("active");
    }

    closeAllModals() {
        document.querySelectorAll(".modal.active").forEach(modal => {
            modal.classList.remove("active");
        });
    }

    showNotification(message, type = "info") {
        // Simple notification system
        const notification = document.createElement("div");
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add("show");
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove("show");
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // ===== MODEL MANAGEMENT =====
    // Model management is now handled by the Models module
    
    updateModelDisplay() {
        const modelsModule = this.moduleLoader.get('models');
        if (modelsModule) {
            modelsModule.updateModelDisplay();
        }
    }

    formatModelName(modelId) {
        const nameMap = {
            'llama-3.1-8b-instant': 'Llama 3.1 8B (Lightning Fast)',
            'llama-3.1-70b-versatile': 'Llama 3.1 70B (Ultra Smart)',
            'llama-3.2-1b-preview': 'Llama 3.2 1B (Compact)',
            'llama-3.2-3b-preview': 'Llama 3.2 3B (Efficient)',
            'mixtral-8x7b-32768': 'Mixtral 8x7B (Expert Mix)',
            'gemma-7b-it': 'Gemma 7B (Google)',
            'gemma2-9b-it': 'Gemma 2 9B (Google Next)'
        };
        
        return nameMap[modelId] || modelId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getProviderDisplayName(providerId) {
        const providerNames = {
            groq: "Groq",
            openai: "OpenAI",
            anthropic: "Anthropic",
            google: "Google",
            ollama: "Ollama",
            huggingface: "Hugging Face"
        };
        
        return providerNames[providerId] || providerId.charAt(0).toUpperCase() + providerId.slice(1);
    }

    // ===== UTILITY METHODS =====
    
    getActiveGuardrails() {
        // Return active guardrails configuration
        return {
            content_safety: true,
            prompt_injection: true,
            pii_detection: true
        };
    }

    // ===== PUBLIC API =====
    
    getModule(name) {
        return this.moduleLoader.get(name);
    }

    isModuleLoaded(name) {
        return this.moduleLoader.isLoaded(name);
    }

    async loadModule(name) {
        return await this.moduleLoader.load(name, this);
    }
}

// Initialize application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    window.nexusAI = new NexusAIModular();
});

export default NexusAIModular;
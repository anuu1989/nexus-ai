/**
 * Main Application Module
 * =======================
 * Modular NexusAI frontend application
 */

import ChatComponent from "./components/chat.js";
import FooterComponent from "./components/footer.js";
import apiService from "./services/api.js";
import storageService from "./services/storage.js";
import { showNotification } from "./utils/notifications.js";

class NexusAI {
  constructor() {
    this.chat = null;
    this.footer = null;
    this.conversations = [];
    this.settings = {};
    this.availableModels = [];

    this.init();
  }

  async init() {
    console.log("🚀 Initializing NexusAI...");

    // Load settings and conversations
    this.settings = storageService.loadSettings();
    this.conversations = storageService.loadConversations();

    // Initialize components
    this.chat = new ChatComponent();
    this.footer = new FooterComponent();

    // Load models
    await this.loadModels();

    // Setup global event listeners
    this.setupGlobalEventListeners();

    // Apply theme
    this.applyTheme();

    console.log("✅ NexusAI initialized successfully");
    showNotification("NexusAI ready!", "success");
  }

  async loadModels() {
    try {
      this.availableModels = await apiService.getModels();
      console.log(`📋 Loaded ${this.availableModels.length} models`);
    } catch (error) {
      console.error("Failed to load models:", error);
      showNotification("Failed to load models", "error");
    }
  }

  setupGlobalEventListeners() {
    // New chat button
    document.getElementById("newChatBtn")?.addEventListener("click", () => {
      this.startNewChat();
    });

    // Settings button
    document.getElementById("settingsBtn")?.addEventListener("click", () => {
      this.openSettings();
    });

    // Sidebar toggle
    document.getElementById("sidebarToggle")?.addEventListener("click", () => {
      this.toggleSidebar();
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      // Ctrl/Cmd + N for new chat
      if ((e.ctrlKey || e.metaKey) && e.key === "n") {
        e.preventDefault();
        this.startNewChat();
      }
    });
  }

  startNewChat() {
    // Clear current chat
    const messagesList = document.getElementById("messagesList");
    if (messagesList) {
      messagesList.innerHTML = "";
    }

    // Show welcome screen
    const welcomeScreen = document.getElementById("welcomeScreen");
    const messagesContainer = document.getElementById("messagesContainer");

    if (welcomeScreen && messagesContainer) {
      welcomeScreen.style.display = "flex";
      messagesContainer.style.display = "none";
    }

    showNotification("New chat started", "success");
  }

  toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar?.classList.toggle("open");
  }

  openSettings() {
    // Simple settings implementation
    const theme = prompt(
      "Choose theme (light/dark/auto):",
      this.settings.theme
    );
    if (theme && ["light", "dark", "auto"].includes(theme)) {
      this.settings.theme = theme;
      storageService.saveSettings(this.settings);
      this.applyTheme();
      showNotification("Settings saved", "success");
    }
  }

  applyTheme() {
    const theme = this.settings.theme || "auto";

    if (theme === "auto") {
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      document.documentElement.setAttribute(
        "data-theme",
        prefersDark ? "dark" : "light"
      );
    } else {
      document.documentElement.setAttribute("data-theme", theme);
    }
  }

  // Public API for external access
  getChat() {
    return this.chat;
  }

  getFooter() {
    return this.footer;
  }

  getSettings() {
    return this.settings;
  }
}

// Initialize application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.nexusAI = new NexusAI();
});

export default NexusAI;

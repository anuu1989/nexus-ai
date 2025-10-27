/**
 * Storage Service Module
 * ======================
 * Handles local storage operations
 */

import CONFIG from '../utils/config.js';

class StorageService {
    /**
     * Save conversations to localStorage
     */
    saveConversations(conversations) {
        try {
            localStorage.setItem(CONFIG.STORAGE.CONVERSATIONS_KEY, JSON.stringify(conversations));
        } catch (error) {
            console.error('Failed to save conversations:', error);
        }
    }

    /**
     * Load conversations from localStorage
     */
    loadConversations() {
        try {
            const stored = localStorage.getItem(CONFIG.STORAGE.CONVERSATIONS_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Failed to load conversations:', error);
            return [];
        }
    }

    /**
     * Save settings to localStorage
     */
    saveSettings(settings) {
        try {
            localStorage.setItem(CONFIG.STORAGE.SETTINGS_KEY, JSON.stringify(settings));
        } catch (error) {
            console.error('Failed to save settings:', error);
        }
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        try {
            const stored = localStorage.getItem(CONFIG.STORAGE.SETTINGS_KEY);
            return stored ? JSON.parse(stored) : this.getDefaultSettings();
        } catch (error) {
            console.error('Failed to load settings:', error);
            return this.getDefaultSettings();
        }
    }

    /**
     * Get default settings
     */
    getDefaultSettings() {
        return {
            theme: 'auto',
            defaultModel: CONFIG.MODELS.DEFAULT,
            autoSave: true,
            compactMode: false
        };
    }

    /**
     * Clear all stored data
     */
    clearAll() {
        try {
            localStorage.removeItem(CONFIG.STORAGE.CONVERSATIONS_KEY);
            localStorage.removeItem(CONFIG.STORAGE.SETTINGS_KEY);
        } catch (error) {
            console.error('Failed to clear storage:', error);
        }
    }
}

// Export singleton instance
export const storageService = new StorageService();
export default storageService;
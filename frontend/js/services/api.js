/**
 * API Service Module
 * ==================
 * Handles all API communications
 */

import CONFIG from '../utils/config.js';

class APIService {
    constructor() {
        this.baseURL = CONFIG.API.BASE_URL;
    }

    /**
     * Send a chat message
     */
    async sendMessage(message, model = CONFIG.MODELS.DEFAULT) {
        try {
            const response = await fetch(CONFIG.API.ENDPOINTS.CHAT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: model
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Get available models
     */
    async getModels() {
        try {
            const response = await fetch(CONFIG.API.ENDPOINTS.MODELS);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.models || [];
        } catch (error) {
            console.error('Models fetch error:', error);
            return [];
        }
    }

    /**
     * Refresh models from providers
     */
    async refreshModels() {
        try {
            const response = await fetch(CONFIG.API.ENDPOINTS.MODELS_REFRESH, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.models || [];
        } catch (error) {
            console.error('Models refresh error:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService;
/**
 * Frontend Configuration
 * =====================
 * Centralized configuration for the frontend
 */

export const CONFIG = {
    API: {
        BASE_URL: '',
        ENDPOINTS: {
            CHAT: '/api/chat',
            MODELS: '/api/models',
            MODELS_REFRESH: '/api/models/refresh'
        }
    },
    
    UI: {
        ANIMATION_DURATION: 300,
        TYPING_DELAY: 150,
        AUTO_SAVE_DELAY: 1000
    },
    
    MODELS: {
        DEFAULT: 'llama-3.1-8b-instant',
        FALLBACK: 'gpt-3.5-turbo'
    },
    
    STORAGE: {
        CONVERSATIONS_KEY: 'nexusai_conversations',
        SETTINGS_KEY: 'nexusai_settings'
    }
};

export default CONFIG;
/**
 * Models Module
 * =============
 * Handles model management, selection, and provider status
 */

class ModelsModule {
    constructor(app) {
        this.app = app;
        this.availableModels = [];
        this.providers = {};
        this.multiProviderEnabled = false;
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.setupModelsEventListeners();
        this.loadAvailableModels();
    }

    setupModelsEventListeners() {
        // Models panel controls
        document.getElementById("refreshModelsBtn")?.addEventListener("click", () => this.refreshModelsFromAPI());
        document.getElementById("compareModelsBtn")?.addEventListener("click", () => this.openModelComparison());
        document.getElementById("aiModelsBtn")?.addEventListener("click", () => this.openModelsModal());
        document.getElementById("modalRefreshModelsBtn")?.addEventListener("click", () => this.refreshModelsInModal());
        document.getElementById("modalCompareModelsBtn")?.addEventListener("click", () => this.openModelComparison());

        // Make model switching available globally for onclick handlers
        window.switchModel = (modelId) => this.switchModel(modelId);
        window.directSwitchModel = (modelId) => this.directSwitchModel(modelId);
    }

    async loadAvailableModels() {
        if (this.isLoading) return;
        
        console.log("🚀 loadAvailableModels called");
        this.isLoading = true;
        
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
                this.availableModels = models;
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

                // Notify app of successful load
                this.app.showNotification(`Loaded ${models.length} models`, "success");
            } else {
                // Fallback to default models
                const defaultModels = this.getDefaultModels();
                this.availableModels = defaultModels;
                this.renderModelsList(defaultModels);
                this.updateModelsStats(defaultModels);
                this.updateMainModelDropdown(defaultModels);
                this.app.showNotification("Using default models (API unavailable)", "warning");
            }
        } catch (error) {
            console.error("Failed to load models:", error);
            const defaultModels = this.getDefaultModels();
            this.availableModels = defaultModels;
            this.renderModelsList(defaultModels);
            this.updateModelsStats(defaultModels);
            this.updateMainModelDropdown(defaultModels);
            this.app.showNotification("Using default models (API unavailable)", "warning");
        } finally {
            this.isLoading = false;
        }
    }

    async refreshModelsFromAPI() {
        console.log("🔄 Forcing real-time model refresh from all provider APIs...");
        
        try {
            const response = await fetch("/api/models/refresh", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("✅ Models refreshed from API:", data);

            if (data.status === "success") {
                this.availableModels = data.models || [];
                this.providers = data.providers || {};
                this.renderModelsList(this.availableModels);
                this.updateModelsStats(this.availableModels);
                this.updateMainModelDropdown(this.availableModels);
                this.updateProviderStatus();

                this.app.showNotification(`Refreshed ${this.availableModels.length} models`, "success");
            } else {
                throw new Error(data.message || "Failed to refresh models");
            }
        } catch (error) {
            console.error("❌ Error refreshing models from API:", error);
            this.app.showNotification("Failed to refresh models", "error");
            // Fallback to regular load
            await this.loadAvailableModels();
        }
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

        const currentModel = this.app.currentModel || "llama-3.1-8b-instant";
        modelsList.innerHTML = "";

        models.forEach((model) => {
            const modelItem = document.createElement("div");
            modelItem.className = `model-item ${model.id === currentModel ? "active" : ""}`;

            const providerBadge = model.provider_name
                ? `<span class="provider-badge provider-${model.provider}" style="background: ${this.getProviderColor(model.provider)}; color: white; font-size: 8px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">${model.provider_name}</span>`
                : "";

            const costInfo = model.cost_per_1k_tokens !== undefined
                ? `<span class="cost-info" style="color: ${model.cost_per_1k_tokens === 0 ? "#4caf50" : "#666"}; font-weight: ${model.cost_per_1k_tokens === 0 ? "600" : "400"};">
                        ${model.cost_per_1k_tokens === 0 ? "🆓 FREE" : `💰 ${model.cost_per_1k_tokens.toFixed(5)}/1K`}
                    </span>`
                : "";

            modelItem.innerHTML = `
                <div class="model-info">
                    <div class="model-header">
                        <div class="model-name">${model.name || model.id}</div>
                        ${providerBadge}
                    </div>
                    <div class="model-description">${model.description || "AI Language Model"}</div>
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

    updateModelsStats(models) {
        const availableModelsCount = document.getElementById("availableModelsCount");
        if (availableModelsCount) {
            availableModelsCount.textContent = models.length;
        }

        // Update provider counts
        const providerCounts = models.reduce((acc, model) => {
            acc[model.provider] = (acc[model.provider] || 0) + 1;
            return acc;
        }, {});

        console.log("📊 Provider counts:", providerCounts);
    }

    updateMainModelDropdown(models) {
        const defaultModelSelect = document.getElementById("defaultModelSelect");
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

    updateProviderStatus() {
        console.log("🎯 updateProviderStatus called", {
            providers: this.providers,
            multiProviderEnabled: this.multiProviderEnabled,
        });

        const providerStatus = document.getElementById("providerStatus");
        if (!providerStatus) return;

        if (!this.providers || Object.keys(this.providers).length === 0) {
            providerStatus.innerHTML = `
                <div class="provider-status-item">
                    <span class="provider-name">Single Provider Mode</span>
                    <span class="provider-status active">Active</span>
                </div>
            `;
            return;
        }

        const enabledProviders = Object.values(this.providers).filter((p) => p.enabled);

        providerStatus.innerHTML = `
            <div class="provider-summary">
                <h6><i class="fas fa-network-wired"></i> Provider Status</h6>
                <div class="provider-count">${enabledProviders.length} Active</div>
            </div>
            <div class="provider-list">
                ${Object.entries(this.providers)
                    .map(([id, provider]) => `
                        <div class="provider-status-item ${provider.enabled ? 'enabled' : 'disabled'}">
                            <span class="provider-name">${provider.name}</span>
                            <span class="provider-status ${provider.enabled ? 'active' : 'inactive'}">
                                ${provider.enabled ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    `).join('')}
            </div>
        `;

        // Update provider hub
        const providerHub = document.getElementById("providerIndicator");
        if (this.providers && providerHub) {
            const enabledProviders = Object.values(this.providers).filter((p) => p.enabled);
            const hubCount = document.getElementById("hubCount");
            const hubStatusText = document.getElementById("hubStatusText");

            if (hubCount) hubCount.textContent = enabledProviders.length;
            if (hubStatusText) hubStatusText.textContent = enabledProviders.length > 1 ? "Multi-AI" : "Single-AI";
        }
    }

    selectModel(modelId) {
        console.log("🎯 selectModel called with:", modelId);
        
        // Update current model
        this.app.currentModel = modelId;
        this.app.settings.defaultModel = modelId;
        this.app.saveSettings();

        // Update UI
        this.updateModelDisplay();
        this.updateModelSelection(modelId);

        // Show notification
        this.app.showNotification(`Switched to ${this.formatModelName(modelId)}`, "success");

        // Close modal if open
        this.closeModelsModal();
    }

    switchModel(modelId) {
        this.selectModel(modelId);
    }

    directSwitchModel(modelId) {
        // Update the model property immediately
        this.app.currentModel = modelId;
        this.app.settings.defaultModel = modelId;
        this.app.saveSettings();

        // Mark that user has explicitly set a model
        this.app._userSelectedModel = true;

        // Force DOM update
        const displayName = this.formatModelName(modelId);
        const element = document.getElementById("currentModelName");
        if (element) {
            element.textContent = displayName;
        }

        // Update UI
        this.updateModelDisplay();
        this.updateModelSelection(modelId);

        this.app.showNotification(`Switched to ${displayName}`, "success");
    }

    updateModelDisplay() {
        const currentModelName = document.getElementById("currentModelName");
        if (currentModelName && this.app.currentModel) {
            const displayName = this.formatModelName(this.app.currentModel);
            currentModelName.textContent = displayName;
        }
    }

    updateModelSelection(modelId) {
        // Update active model in lists
        document.querySelectorAll(".model-item").forEach(item => {
            const itemModelId = item.dataset.modelId;
            if (itemModelId === modelId) {
                item.classList.add("active");
                const btn = item.querySelector(".model-select-btn");
                if (btn) btn.textContent = "Active";
            } else {
                item.classList.remove("active");
                const btn = item.querySelector(".model-select-btn");
                if (btn) btn.textContent = "Select";
            }
        });
    }

    formatModelName(modelId) {
        const nameMap = {
            'llama-3.1-8b-instant': 'Llama 3.1 8B (Lightning Fast)',
            'llama-3.1-70b-versatile': 'Llama 3.1 70B (Ultra Smart)',
            'llama-3.2-1b-preview': 'Llama 3.2 1B (Compact)',
            'llama-3.2-3b-preview': 'Llama 3.2 3B (Efficient)',
            'llama-3.2-11b-text-preview': 'Llama 3.2 11B (Balanced)',
            'llama-3.2-90b-text-preview': 'Llama 3.2 90B (Powerful)',
            'llama-3.2-11b-vision-preview': 'Llama 3.2 Vision (Image AI)',
            'llama-3.2-90b-vision-preview': 'Llama 3.2 Vision Pro (Advanced)',
            'mixtral-8x7b-32768': 'Mixtral 8x7B (Expert Mix)',
            'gemma-7b-it': 'Gemma 7B (Google)',
            'gemma2-9b-it': 'Gemma 2 9B (Google Next)',
            'gpt-4o': 'GPT-4 Omni (OpenAI)',
            'gpt-4o-mini': 'GPT-4 Omni Mini (OpenAI)',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo (OpenAI)',
            'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet (Anthropic)',
            'claude-3-haiku-20240307': 'Claude 3 Haiku (Anthropic)'
        };
        
        return nameMap[modelId] || modelId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getProviderColor(providerId) {
        const colors = {
            groq: "#f97316",
            openai: "#10b981", 
            anthropic: "#8b5cf6",
            google: "#3b82f6",
            ollama: "#6b7280",
            huggingface: "#fbbf24"
        };
        return colors[providerId] || "#6b7280";
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
                cost_per_1k_tokens: 0.00005
            },
            {
                id: "llama-3.1-70b-versatile",
                name: "Llama 3.1 70B (Smart)",
                description: "Advanced reasoning for complex problems",
                provider: "groq",
                provider_name: "Groq",
                supportsVision: false,
                cost_per_1k_tokens: 0.0002
            },
            {
                id: "llama-3.2-11b-vision-preview",
                name: "Llama 3.2 Vision",
                description: "Image analysis and visual reasoning",
                provider: "groq",
                provider_name: "Groq",
                supportsVision: true,
                cost_per_1k_tokens: 0.00018
            }
        ];
    }

    // Modal management
    openModelsModal() {
        const modal = document.getElementById("aiModelsModal");
        if (modal) {
            modal.classList.add("active");
            this.loadModalModelGrid();
        }
    }

    closeModelsModal() {
        const modal = document.getElementById("aiModelsModal");
        if (modal) {
            modal.classList.remove("active");
        }
    }

    async loadModalModelGrid() {
        // Always refresh models when opening modal to ensure real-time data
        console.log("🔄 Refreshing models for modal...");
        try {
            await this.refreshModelsFromAPI();
            console.log("✅ Models refreshed from API, now updating modal grid");
            this.updateModalGrid();
        } catch (error) {
            console.error("❌ Error refreshing models from API:", error);
            // Fallback to regular load
            await this.loadAvailableModels();
            this.updateModalGrid();
        }
    }

    updateModalGrid() {
        const modalGrid = document.getElementById("modalModelGrid");
        if (!modalGrid) return;

        const models = this.availableModels;
        const currentModel = this.app.currentModel;

        let gridHTML = "";
        
        // Group models by provider
        const modelsByProvider = models.reduce((acc, model) => {
            if (!acc[model.provider]) acc[model.provider] = [];
            acc[model.provider].push(model);
            return acc;
        }, {});

        // Render each provider section
        Object.entries(modelsByProvider).forEach(([provider, providerModels]) => {
            gridHTML += `
                <div class="provider-section">
                    <h4 class="provider-title">
                        <span class="provider-badge provider-${provider}" style="background: ${this.getProviderColor(provider)}">
                            ${this.getProviderDisplayName(provider)}
                        </span>
                        <span class="model-count">${providerModels.length} models</span>
                    </h4>
                    <div class="models-grid">
            `;

            // Provider models
            providerModels.forEach((model) => {
                const isSelected = model.id === currentModel;
                const modelName = model.name || this.formatModelName(model.id);
                const modelDescription = model.description || "Advanced AI language model";
                const costInfo = model.cost_per_1k_tokens !== undefined
                    ? (model.cost_per_1k_tokens === 0 ? "🆓 FREE" : `💰 $${model.cost_per_1k_tokens.toFixed(5)}/1K`)
                    : "";

                gridHTML += `
                    <div class="model-card ${isSelected ? "selected" : ""}" 
                         data-model-id="${model.id}"
                         onclick="window.directSwitchModel('${model.id}')">
                        <div class="model-card-header">
                            <div class="model-card-name">${modelName}</div>
                            ${isSelected ? '<div class="selected-indicator">✓ Active</div>' : ''}
                        </div>
                        <div class="model-card-description">${modelDescription}</div>
                        <div class="model-card-footer">
                            <div class="model-capabilities">
                                ${model.supportsVision ? '<span class="capability-badge vision">👁️ Vision</span>' : ''}
                                ${model.capabilities?.includes('code') ? '<span class="capability-badge code">💻 Code</span>' : ''}
                            </div>
                            <div class="model-cost">${costInfo}</div>
                        </div>
                    </div>
                `;
            });

            gridHTML += `
                    </div>
                </div>
            `;
        });

        modalGrid.innerHTML = gridHTML;
    }

    getProviderDisplayName(providerId) {
        const providerNames = {
            groq: "Groq",
            openai: "OpenAI", 
            anthropic: "Anthropic",
            google: "Google AI",
            ollama: "Ollama",
            huggingface: "Hugging Face"
        };
        
        return providerNames[providerId] || providerId.charAt(0).toUpperCase() + providerId.slice(1);
    }

    async refreshModelsInModal() {
        const refreshBtn = document.getElementById("modalRefreshModelsBtn");
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
        }

        try {
            await this.loadAvailableModels();
            this.updateModalGrid();
            this.app.showNotification("Models refreshed successfully", "success");
        } catch (error) {
            console.error("Error refreshing models in modal:", error);
            this.app.showNotification("Failed to refresh models", "error");
        } finally {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh Models';
                refreshBtn.disabled = false;
            }
        }
    }

    openModelComparison() {
        // TODO: Implement model comparison functionality
        this.app.showNotification("Model comparison coming soon!", "info");
    }

    // Public API
    getAvailableModels() {
        return this.availableModels;
    }

    getCurrentModel() {
        return this.app.currentModel;
    }

    getProviders() {
        return this.providers;
    }

    isMultiProviderEnabled() {
        return this.multiProviderEnabled;
    }

    cleanup() {
        // Cleanup when module is unloaded
        window.switchModel = null;
        window.directSwitchModel = null;
    }
}

export default ModelsModule;
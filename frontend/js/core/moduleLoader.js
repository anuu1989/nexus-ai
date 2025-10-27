/**
 * Module Loader
 * =============
 * Manages loading and initialization of modular components
 */

class ModuleLoader {
    constructor() {
        this.modules = new Map();
        this.loadedModules = new Set();
    }

    /**
     * Register a module for loading
     * @param {string} name - Module name
     * @param {string} path - Module file path
     * @param {Array} dependencies - Array of module names this module depends on
     */
    register(name, path, dependencies = []) {
        this.modules.set(name, {
            name,
            path,
            dependencies,
            instance: null,
            loaded: false
        });
    }

    /**
     * Load a module and its dependencies
     * @param {string} name - Module name to load
     * @param {Object} context - Context object to pass to module constructor
     */
    async load(name, context = null) {
        if (this.loadedModules.has(name)) {
            return this.modules.get(name).instance;
        }

        const moduleInfo = this.modules.get(name);
        if (!moduleInfo) {
            throw new Error(`Module '${name}' not registered`);
        }

        // Load dependencies first
        for (const dep of moduleInfo.dependencies) {
            await this.load(dep, context);
        }

        try {
            // Dynamic import for ES6 modules
            const moduleExport = await import(moduleInfo.path);
            const ModuleClass = moduleExport.default;
            
            // Create instance with context
            const instance = new ModuleClass(context);
            
            moduleInfo.instance = instance;
            moduleInfo.loaded = true;
            this.loadedModules.add(name);
            
            console.log(`✅ Module '${name}' loaded successfully`);
            return instance;
            
        } catch (error) {
            console.error(`❌ Failed to load module '${name}':`, error);
            throw error;
        }
    }

    /**
     * Get a loaded module instance
     * @param {string} name - Module name
     */
    get(name) {
        const moduleInfo = this.modules.get(name);
        return moduleInfo?.instance || null;
    }

    /**
     * Check if a module is loaded
     * @param {string} name - Module name
     */
    isLoaded(name) {
        return this.loadedModules.has(name);
    }

    /**
     * Load all registered modules
     * @param {Object} context - Context object to pass to module constructors
     */
    async loadAll(context = null) {
        const loadPromises = Array.from(this.modules.keys()).map(name => 
            this.load(name, context)
        );
        
        try {
            await Promise.all(loadPromises);
            console.log(`✅ All modules loaded successfully`);
        } catch (error) {
            console.error(`❌ Failed to load some modules:`, error);
            throw error;
        }
    }

    /**
     * Unload a module
     * @param {string} name - Module name
     */
    unload(name) {
        const moduleInfo = this.modules.get(name);
        if (moduleInfo && moduleInfo.instance) {
            // Call cleanup method if it exists
            if (typeof moduleInfo.instance.cleanup === 'function') {
                moduleInfo.instance.cleanup();
            }
            
            moduleInfo.instance = null;
            moduleInfo.loaded = false;
            this.loadedModules.delete(name);
            
            console.log(`✅ Module '${name}' unloaded`);
        }
    }

    /**
     * Get information about all modules
     */
    getModuleInfo() {
        const info = {};
        for (const [name, moduleInfo] of this.modules) {
            info[name] = {
                name: moduleInfo.name,
                loaded: moduleInfo.loaded,
                dependencies: moduleInfo.dependencies,
                hasInstance: moduleInfo.instance !== null
            };
        }
        return info;
    }
}

export default ModuleLoader;
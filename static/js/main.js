/**
 * Main Application Entry Point
 * Initializes and coordinates all modules
 */
console.log('Main script loading...');

// Track module initialization
const initializeModule = (module, name) => {
    console.group(`Initializing ${name} module`);
    try {
        if (!module) {
            throw new Error(`${name} module not found`);
        }
        module.init();
        console.log(`${name} module initialized successfully`);
    } catch (error) {
        console.error(`Error initializing ${name} module:`, error);
    }
    console.groupEnd();
};

// Initialize all modules when DOM is ready
$(document).ready(() => {
    console.group('Initializing application modules');
    
    // Initialize modules in dependency order
    initializeModule(window.LoyaltyPrograms, 'LoyaltyPrograms');
    initializeModule(window.TripTypes, 'TripTypes');
    initializeModule(window.DepartingAirports, 'DepartingAirports');
    initializeModule(window.TripInfo, 'TripInfo');
    initializeModule(window.TripGenerator, 'TripGenerator');
    
    console.groupEnd();
    console.log('All modules initialized');
});

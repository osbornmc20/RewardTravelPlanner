// Initialize all modules
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure all modules are loaded
    setTimeout(() => {
        console.log('Initializing modules...');
        if (window.LoyaltyPrograms) window.LoyaltyPrograms.init();
        if (window.TripTypes) window.TripTypes.init();
        if (window.DepartingAirports) window.DepartingAirports.init();
        if (window.TripInfo) window.TripInfo.init();
        if (window.TripGenerator) window.TripGenerator.init();
        console.log('All modules initialized');
    }, 100);
});

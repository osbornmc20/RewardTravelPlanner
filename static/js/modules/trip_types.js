/**
 * Trip Types Module
 * Handles trip type selection functionality
 */
const TripTypes = {
    initialized: false,
    maxTripTypes: 2,
    selectedTypes: new Set(),

    init() {
        if (this.initialized) {
            console.warn('TripTypes module already initialized');
            return;
        }
        console.log('Initializing TripTypes module');

        // Bind click handlers
        $('.trip-type-box').click(this.handleTripTypeClick.bind(this));

        this.initialized = true;
        console.log('TripTypes module initialized');
    },

    handleTripTypeClick(e) {
        const box = $(e.currentTarget);
        console.log('Trip type clicked:', box.data('type'));

        if (box.hasClass('disabled')) {
            console.log('Box is disabled, ignoring click');
            return;
        }

        const tripType = box.data('type');
        
        if (box.hasClass('selected')) {
            console.log('Deselecting trip type:', tripType);
            box.removeClass('selected');
            this.selectedTypes.delete(tripType);
        } else if (this.selectedTypes.size < this.maxTripTypes) {
            console.log('Selecting trip type:', tripType);
            box.addClass('selected');
            this.selectedTypes.add(tripType);
        }

        this.updateTripTypeStates();
    },

    updateTripTypeStates() {
        console.log('Updating trip type states. Selected types:', Array.from(this.selectedTypes));
        
        $('.trip-type-box').each((_, box) => {
            const $box = $(box);
            if (!$box.hasClass('selected') && this.selectedTypes.size >= this.maxTripTypes) {
                $box.addClass('disabled');
            } else {
                $box.removeClass('disabled');
            }
        });
    },

    getSelectedTypes() {
        return Array.from(this.selectedTypes);
    }
};

// Export the module
window.TripTypes = TripTypes;

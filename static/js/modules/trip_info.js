/**
 * Trip Information Module
 * Handles trip information form functionality
 */
const TripInfo = {
    initialized: false,

    init() {
        if (this.initialized) {
            console.warn('TripInfo module already initialized');
            return;
        }
        console.log('Initializing TripInfo module');

        // Set up numeric input validation
        $('#tripLength').on('input', this.validateNumericInput.bind(this));
        $('#maxFlightLength').on('input', this.validateNumericInput.bind(this));

        this.initialized = true;
        console.log('TripInfo module initialized');
    },

    validateNumericInput(e) {
        const input = $(e.target);
        const value = input.val();
        
        console.log('Validating numeric input:', { id: input.attr('id'), value });

        if (value && (isNaN(value) || value <= 0)) {
            alert('Please enter a positive number');
            input.val('');
        }
    },

    getTripInfo() {
        console.log('Getting trip information');
        const tripLength = parseInt($('#tripLength').val(), 10);
        const maxFlightLength = parseInt($('#maxFlightLength').val(), 10);
        
        const tripInfo = {
            travel_months: $('#travelMonths').val(),
            trip_length: isNaN(tripLength) ? null : tripLength,
            max_flight_length: isNaN(maxFlightLength) ? null : maxFlightLength,
            direct_flights: $('#directFlights').is(':checked'),
            preferences: $('#specialRequests').val() || ''
        };
        console.log('Trip info collected:', tripInfo);
        return tripInfo;
    },

    validateTripInfo() {
        const info = this.getTripInfo();
        const errors = [];

        // Required fields
        if (!info.travel_months) errors.push('Preferred travel months are required');
        if (!info.trip_length) errors.push('Trip length is required');
        if (!info.max_flight_length) errors.push('Maximum flight length is required');

        // Numeric validation
        if (info.trip_length && (isNaN(info.trip_length) || info.trip_length <= 0)) {
            errors.push('Trip length must be a positive number');
        }
        if (info.max_flight_length && (isNaN(info.max_flight_length) || info.max_flight_length <= 0)) {
            errors.push('Maximum flight length must be a positive number');
        }

        console.log('Trip info validation results:', { info, errors });
        return errors;
    }
};

// Export the module
window.TripInfo = TripInfo;

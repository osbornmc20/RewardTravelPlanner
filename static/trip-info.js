$(document).ready(function() {
    const startDateInput = $('#startDate');
    const endDateInput = $('#endDate');
    const tripLengthInput = $('#tripLength');
    
    // Set minimum date to today
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const maxDate = new Date(today);
    maxDate.setFullYear(maxDate.getFullYear() + 1);
    
    startDateInput.attr('min', tomorrow.toISOString().split('T')[0]);
    startDateInput.attr('max', maxDate.toISOString().split('T')[0]);
    endDateInput.attr('min', tomorrow.toISOString().split('T')[0]);
    endDateInput.attr('max', maxDate.toISOString().split('T')[0]);
    
    // Update end date min value when start date changes
    startDateInput.change(function() {
        const startDate = new Date(this.value);
        const minEndDate = new Date(startDate);
        minEndDate.setDate(startDate.getDate() + 1);
        
        endDateInput.attr('min', minEndDate.toISOString().split('T')[0]);
        
        // If end date is now invalid, clear it
        if (endDateInput.val() && new Date(endDateInput.val()) <= startDate) {
            endDateInput.val('');
        }
        
        updateTripLength();
    });
    
    // Update trip length when end date changes
    endDateInput.change(function() {
        updateTripLength();
    });
    
    // Update dates when trip length changes
    tripLengthInput.change(function() {
        const length = parseInt($(this).val());
        const startDate = new Date(startDateInput.val());
        
        if (startDate && !isNaN(length) && length > 0 && length <= 30) {
            const endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + length - 1);
            endDateInput.val(endDate.toISOString().split('T')[0]);
        }
    });
    
    function updateTripLength() {
        const startDate = new Date(startDateInput.val());
        const endDate = new Date(endDateInput.val());
        
        if (startDate && endDate && endDate > startDate) {
            const diffTime = Math.abs(endDate - startDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
            tripLengthInput.val(diffDays);
        }
    }
    
    // Form validation
    $('#tripInfoForm').on('submit', function(e) {
        e.preventDefault();
        
        const startDate = new Date(startDateInput.val());
        const endDate = new Date(endDateInput.val());
        const tripLength = parseInt(tripLengthInput.val());
        
        if (!startDate || !endDate || isNaN(tripLength)) {
            alert('Please fill in all required fields');
            return;
        }
        
        if (endDate <= startDate) {
            alert('End date must be after start date');
            return;
        }
        
        if (tripLength < 1 || tripLength > 30) {
            alert('Trip length must be between 1 and 30 days');
            return;
        }
    });
});

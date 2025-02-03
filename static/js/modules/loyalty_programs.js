/**
 * Loyalty Programs Module
 * Handles all loyalty program related functionality
 */
const LoyaltyPrograms = {
    initialized: false,

    init() {
        if (this.initialized) {
            console.warn('LoyaltyPrograms module already initialized');
            return;
        }
        console.log('Initializing LoyaltyPrograms module');

        // Hide all program selects initially
        $('.program-select').hide();

        // Program Type Selection Handler
        $('#programType').change(this.handleProgramTypeChange.bind(this));

        // Add New Program Form Submission
        $('#add-program-form').on('submit', this.handleAddProgram.bind(this));

        // Update Points Balance
        $('.update-points-form').on('submit', this.handleUpdatePoints.bind(this));

        // Delete Program
        $('.delete-program').click(this.handleDeleteProgram.bind(this));

        this.initialized = true;
        console.log('LoyaltyPrograms module initialized');
    },

    handleProgramTypeChange(e) {
        const programType = $(e.target).val();
        console.log('Program type changed to:', programType);
        
        // Hide all program selects first
        $('.program-select').hide();
        
        // Show the relevant program select based on type
        switch(programType) {
            case 'airline':
                $('#airlineSelect').show();
                break;
            case 'hotel':
                $('#hotelSelect').show();
                break;
            case 'creditcard':
                $('#creditCardSelect').show();
                break;
        }
    },

    handleAddProgram(e) {
        e.preventDefault();
        console.log('Adding new loyalty program');
        
        const programType = $('#programType').val();
        let programName;
        
        // Get the selected program name based on type
        switch(programType) {
            case 'airline':
                programName = $('#airlineProgram').val();
                break;
            case 'hotel':
                programName = $('#hotelProgram').val();
                break;
            case 'creditcard':
                programName = $('#creditCardProgram').val();
                break;
            default:
                alert('Please select a program type');
                return;
        }
        
        if (!programName) {
            alert('Please select a program');
            return;
        }

        const pointsBalance = $('#points-balance').val();
        if (!pointsBalance || pointsBalance < 0) {
            alert('Please enter a valid points balance');
            return;
        }
        
        const formData = {
            program_type: programType,
            program_name: programName,
            points_balance: parseInt(pointsBalance)
        };

        console.log('Submitting program data:', formData);

        $.ajax({
            url: '/points/add',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Error adding program: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error adding program:', error);
                alert('Error adding program. Please try again.');
            }
        });
    },

    handleUpdatePoints(e) {
        e.preventDefault();
        const form = $(e.currentTarget);
        const programId = form.data('program-id');
        console.log('Updating points for program:', programId);

        const pointsBalance = form.find('.points-input').val();
        if (!pointsBalance || pointsBalance < 0) {
            alert('Please enter a valid points balance');
            return;
        }

        const formData = {
            id: programId,
            points: parseInt(pointsBalance)
        };

        $.ajax({
            url: '/points/update',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Error updating points: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error updating points:', error);
                alert('Error updating points. Please try again.');
            }
        });
    },

    handleDeleteProgram(e) {
        const programId = $(e.currentTarget).data('program-id');
        console.log('Deleting program:', programId);

        if (confirm('Are you sure you want to delete this program?')) {
            $.ajax({
                url: '/points/delete',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ id: programId }),
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert('Error deleting program: ' + response.error);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error deleting program:', error);
                    alert('Error deleting program. Please try again.');
                }
            });
        }
    }
};

// Initialize when document is ready
$(document).ready(() => {
    LoyaltyPrograms.init();
});

// Export the module
window.LoyaltyPrograms = LoyaltyPrograms;

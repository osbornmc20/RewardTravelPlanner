$(document).ready(function() {
    console.log('Airport search initialized');
    const selectedAirports = new Set();
    const maxAirports = 3;
    
    function displaySelectedAirports() {
        console.log('Displaying selected airports:', selectedAirports);
        const container = $('#selected-airports');
        container.empty();
        
        selectedAirports.forEach(airport => {
            const airportDiv = $('<div>')
                .addClass('selected-airport')
                .html(`
                    <span><strong>${airport.code}</strong> - ${airport.name}</span>
                    <button type="button" class="btn btn-sm btn-danger" 
                            onclick="removeAirport('${airport.code}')">×</button>
                `);
            container.append(airportDiv);
        });
        
        if (selectedAirports.size >= maxAirports) {
            $('#airport-input-wrapper').hide();
        } else {
            $('#airport-input-wrapper').show();
        }
    }
    
    window.removeAirport = function(code) {
        console.log('Removing airport:', code);
        selectedAirports.forEach(airport => {
            if (airport.code === code) {
                selectedAirports.delete(airport);
            }
        });
        displaySelectedAirports();
    };
    
    function addAirport(airport) {
        console.log('Adding airport:', airport);
        if (selectedAirports.size < maxAirports) {
            let alreadyExists = false;
            selectedAirports.forEach(existing => {
                if (existing.code === airport.code) {
                    alreadyExists = true;
                }
            });
            
            if (!alreadyExists) {
                selectedAirports.add(airport);
                displaySelectedAirports();
                $('#airport-input').val('');
            }
        }
    }
    
    $('#airport-input').on('input', function() {
        console.log('Input event triggered');
        const input = $(this).val().toLowerCase();
        const suggestions = $('#airport-suggestions');
        
        if (input.length < 2) {
            suggestions.hide();
            return;
        }
        
        console.log('Searching for:', input);
        const matches = airports.filter(airport => 
            airport.code.toLowerCase().includes(input) ||
            airport.city.toLowerCase().includes(input) ||
            airport.name.toLowerCase().includes(input)
        ).slice(0, 5);
        
        console.log('Found matches:', matches);
        if (matches.length > 0) {
            suggestions.empty();
            matches.forEach(airport => {
                const div = $('<div>')
                    .addClass('airport-suggestion')
                    .text(`${airport.code} - ${airport.city} (${airport.name})`)
                    .on('click', () => {
                        addAirport(airport);
                        suggestions.hide();
                    });
                suggestions.append(div);
            });
            suggestions.show();
        } else {
            suggestions.hide();
        }
    });
    
    // Hide suggestions when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.airport-input-container').length) {
            $('#airport-suggestions').hide();
        }
    });
});

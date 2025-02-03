console.log(' TRIP PLANNER SCRIPT - STARTING TO LOAD');

// Debug: Check if airports array is available
console.log('Airports array available:', typeof airports !== 'undefined', airports ? airports.length : 0);

document.addEventListener('DOMContentLoaded', function() {
    console.log(' TRIP PLANNER SCRIPT - DOM LOADED');
    
    // Initialize variables
    let selectedTypes = new Set();
    let typingTimer;
    const doneTypingInterval = 300;
    
    // Trip Types functionality
    const tripTypeBoxes = document.querySelectorAll('.trip-type-box');
    console.log('Found trip type boxes:', tripTypeBoxes.length);
    
    tripTypeBoxes.forEach(box => {
        box.addEventListener('click', function() {
            const tripType = this.dataset.type;
            console.log('Trip type clicked:', tripType);
            
            if (this.classList.contains('disabled')) {
                return;
            }
            
            if (this.classList.contains('selected')) {
                this.classList.remove('selected');
                selectedTypes.delete(tripType);
            } else {
                if (selectedTypes.size >= 2) {
                    console.log('Already have 2 trip types selected');
                    return;
                }
                this.classList.add('selected');
                selectedTypes.add(tripType);
            }
            
            updateTripTypeBoxes();
        });
    });
    
    function updateTripTypeBoxes() {
        console.log('Updating trip type boxes. Selected:', selectedTypes);
        tripTypeBoxes.forEach(box => {
            if (!box.classList.contains('selected') && selectedTypes.size >= 2) {
                box.classList.add('disabled');
            } else {
                box.classList.remove('disabled');
            }
        });
    }
    
    // Airport search functionality
    const airportInputs = document.querySelectorAll('.airport-input');
    console.log('Found airport inputs:', airportInputs.length);
    
    airportInputs.forEach((input, index) => {
        console.log(`Setting up airport input ${index}:`, input);
        // Get the parent airport-input-group and find the suggestions container within it
        const inputGroup = input.closest('.airport-input-group');
        const suggestionsContainer = inputGroup.querySelector('.airport-suggestions');
        console.log(`Suggestions container for input ${index}:`, suggestionsContainer);
        
        input.addEventListener('input', function() {
            clearTimeout(typingTimer);
            const query = this.value.toUpperCase();
            console.log(`Airport search query for input ${index}:`, query);
            
            if (query.length >= 2) {
                // Debug: Log the airports array again
                console.log('Airports array when searching:', typeof airports !== 'undefined', airports ? airports.length : 0);
                
                // Filter airports based on the query
                const matchingAirports = airports.filter(airport => 
                    airport.code.includes(query) || 
                    airport.city.toUpperCase().includes(query) ||
                    airport.name.toUpperCase().includes(query)
                ).slice(0, 10); // Limit to 10 results
                
                console.log(`Found ${matchingAirports.length} matching airports for input ${index}:`, matchingAirports);
                
                // Display suggestions
                suggestionsContainer.innerHTML = '';
                matchingAirports.forEach(airport => {
                    const div = document.createElement('div');
                    div.className = 'suggestion';
                    div.textContent = `${airport.code} - ${airport.name}, ${airport.city}`;
                    div.addEventListener('click', () => {
                        input.value = `${airport.code} - ${airport.name}, ${airport.city}`;
                        // Also update the hidden input
                        const hiddenInput = inputGroup.querySelector('.airport-code');
                        if (hiddenInput) {
                            hiddenInput.value = airport.code;
                        }
                        suggestionsContainer.style.display = 'none';
                    });
                    suggestionsContainer.appendChild(div);
                });
                
                console.log(`Suggestions container HTML for input ${index}:`, suggestionsContainer.innerHTML);
                suggestionsContainer.style.display = matchingAirports.length > 0 ? 'block' : 'none';
            } else {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });
    });
    
    // Get required elements
    const generateButton = document.getElementById('generateTripIdeas');
    const resultsContainer = document.getElementById('trip-results');
    
    if (!generateButton) {
        console.error('Generate button not found! ID: generateTripIdeas');
        return;
    }
    
    if (!resultsContainer) {
        console.error('Results container not found! ID: trip-results');
        return;
    }
    
    console.log('Found required elements:', {
        generateButton,
        resultsContainer
    });
    
    generateButton.addEventListener('click', async function(event) {
        event.preventDefault();
        console.log('Generate button clicked');
        
        try {
            generateButton.disabled = true;
            generateButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            
            // Collect trip data
            const tripData = {
                trip_types: Array.from(selectedTypes),
                airports: Array.from(document.querySelectorAll('.airport-input'))
                    .map(input => input.value.trim())
                    .filter(code => code),
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value,
                trip_length: document.getElementById('tripLength').value,
                max_flight_length: document.getElementById('maxFlightLength').value,
                direct_flights: document.getElementById('directFlights').checked,
                user_preferences: document.getElementById('userPreferences').value || ''
            };

            console.log('Sending trip data:', tripData);
            
            const response = await fetch('/generate_trip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(tripData)
            });

            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            let errorMessage;
            try {
                const data = await response.json();
                console.log('Response data:', data);
                
                if (!response.ok || !data.success) {
                    errorMessage = data.error || 'Failed to generate trip';
                    throw new Error(errorMessage);
                }
                
                // Update results container
                displayTripResults(data);
            } catch (jsonError) {
                if (jsonError.message === errorMessage) {
                    throw jsonError;
                }
                // If we can't parse JSON, try to get the text
                const text = await response.text();
                console.error('Response text:', text);
                throw new Error('Server error occurred. Please try again.');
            }
        } catch (error) {
            console.error('Error generating trip:', error);
            const resultsContainer = document.getElementById('trip-results');
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${error.message || 'An unexpected error occurred. Please try again.'}
                </div>
            `;
        } finally {
            generateButton.disabled = false;
            generateButton.innerHTML = 'Generate Trip Ideas';
        }
    });

    function displayTripResults(data) {
        const resultsContainer = document.getElementById('trip-results');
        console.log('Displaying trip results. Data:', data);
        
        resultsContainer.innerHTML = ''; // Clear previous results

        if (!data || !data.success || data.error) {
            console.error('Error in trip results:', data);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${data?.error || 'Failed to generate trip results'}
                </div>
            `;
            return;
        }

        // Get the travel plan content (try both keys for backward compatibility)
        const travelPlan = data.result || data.travel_plan;
        
        // Only try to process results if we have them
        if (!travelPlan || typeof travelPlan !== 'string' || !travelPlan.trim()) {
            resultsContainer.innerHTML = `
                <div class="alert alert-warning">
                    <strong>Note:</strong> No trip results available
                </div>
            `;
            return;
        }

        console.log('Processing travel plan:', travelPlan);
        
        // Split on DESTINATION followed by a number, but keep the destination number and name
        const destinations = travelPlan.split(/(?=DESTINATION \d+)/g)
            .filter(d => d.trim())
            .map(d => d.trim());
        console.log('Found destinations:', destinations);
        
        destinations.forEach((destination, index) => {
            const destinationDiv = document.createElement('div');
            destinationDiv.className = 'trip-section mb-4';
            
            // Extract destination name and preference match
            const lines = destination.trim().split('\n');
            const destinationLine = lines[0].trim(); // This will be "DESTINATION X - City, Country"
            const destinationParts = destinationLine.split(' - ');
            const destinationName = destinationParts[1] || ''; // Get everything after the first ' - '
            
            // Find the preference match line
            const preferenceMatch = lines.find(line => line.trim().startsWith('Preference Match:')) || '';
            
            // Split into economy and luxury experiences using identical patterns
            const economyExp = (destination.match(/OPTION A - ECONOMY EXPERIENCE([\s\S]*?)(?=OPTION B - LUXURY EXPERIENCE|$)/i) || [])[1] || '';
            const luxuryExp = (destination.match(/OPTION B - LUXURY EXPERIENCE([\s\S]*?)(?=DESTINATION|$)/i) || [])[1] || '';
            
            console.log('Economy pattern:', /OPTION A - ECONOMY EXPERIENCE([\s\S]*?)(?=OPTION B - LUXURY EXPERIENCE|$)/i);
            console.log('Economy text found:', economyExp);
            console.log('Luxury text found:', luxuryExp);
            
            destinationDiv.innerHTML = `
                <h3 class="mb-3">Destination ${index + 1} - ${destinationName}</h3>
                <p class="preference-match mb-4">${preferenceMatch}</p>
                
                <div class="trip-experiences">
                    <div class="economy-experience">
                        <h4 class="experience-header">Economy Experience</h4>
                        ${formatExperience(economyExp)}
                    </div>
                    
                    <div class="luxury-experience">
                        <h4 class="experience-header">Luxury Experience</h4>
                        ${formatExperience(luxuryExp)}
                    </div>
                </div>
            `;
            
            resultsContainer.appendChild(destinationDiv);
        });
    }
    
    function formatExperience(experienceText) {
        if (!experienceText) return '';
        
        const sections = experienceText.split(/(?=Flight Details:|Hotel Option:|Value Analysis:)/g)
            .filter(section => section.trim()); // Remove empty sections
        
        return sections.map(section => {
            const lines = section.trim().split('\n');
            const title = lines[0];
            const content = lines.slice(1);
            
            const sectionContent = content
                .filter(line => line.trim()) // Remove empty lines
                .map(line => {
                    const trimmedLine = line.trim();
                    
                    if (trimmedLine.startsWith('-')) {
                        const [label, ...valueParts] = trimmedLine.substring(1).split(':');
                        const value = valueParts.join(':').trim();
                        return `
                            <div class="detail-row">
                                <span class="detail-label">${label.trim()}</span>
                                <span class="detail-value">${value || ''}</span>
                            </div>
                        `;
                    } else if (trimmedLine.startsWith('*')) {
                        const [label, ...valueParts] = trimmedLine.substring(1).split(':');
                        const value = valueParts.join(':').trim();
                        return `
                            <div class="detail-row ${label.trim()}">
                                <span class="detail-label">${label.trim()}</span>
                                <span class="detail-value">${value || ''}</span>
                            </div>
                        `;
                    }
                    return `<div class="detail-text">${trimmedLine}</div>`;
                })
                .join('');
            
            // Only render section if it has content
            if (!sectionContent.trim()) return '';
            
            return `
                <div class="section">
                    <h5 class="section-title">${title}</h5>
                    <div class="section-content">
                        ${sectionContent}
                    </div>
                </div>
            `;
        }).join('');
    }
});

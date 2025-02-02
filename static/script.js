document.addEventListener('DOMContentLoaded', () => {
    // Modal handling
    const modal = document.getElementById('pointsModal');
    const addPointsBtn = document.getElementById('addPointsBtn');
    const closeModal = document.getElementById('closeModal');
    
    addPointsBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });
    
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Form handling
    const addPointsForm = document.getElementById('addPointsForm');
    const tripPlannerForm = document.getElementById('tripPlannerForm');
    const pointsPrograms = document.getElementById('pointsPrograms');
    const tripSuggestions = document.getElementById('tripSuggestions');

    // Set minimum date for date inputs to today
    const today = new Date();
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 1); // Allow booking up to 1 year in advance
    
    const dateRangeStart = document.getElementById('dateRangeStart');
    const dateRangeEnd = document.getElementById('dateRangeEnd');
    
    dateRangeStart.min = today.toISOString().split('T')[0];
    dateRangeStart.max = maxDate.toISOString().split('T')[0];
    dateRangeEnd.min = today.toISOString().split('T')[0];
    dateRangeEnd.max = maxDate.toISOString().split('T')[0];
    
    // Update end date min value when start date changes
    dateRangeStart.addEventListener('change', () => {
        dateRangeEnd.min = dateRangeStart.value;
    });

    loadPointsPrograms();

    // Trip type selection handling
    const tripTypeCheckboxes = document.querySelectorAll('input[name="tripType"]');
    const MAX_TRIP_TYPES = 2;

    tripTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedBoxes = document.querySelectorAll('input[name="tripType"]:checked');
            
            if (checkedBoxes.length > MAX_TRIP_TYPES) {
                this.checked = false;
                return;
            }
            
            // Disable remaining checkboxes if max is reached
            tripTypeCheckboxes.forEach(cb => {
                if (!cb.checked) {
                    cb.disabled = checkedBoxes.length >= MAX_TRIP_TYPES;
                }
            });
        });
    });

    // Airport handling
    const departureAirports = document.querySelector('.departure-airports');
    const addAirportBtn = document.querySelector('.add-airport-btn');
    const MAX_AIRPORTS = 1;
    let selectedAirports = [];

    function createAirportInput() {
        const container = document.createElement('div');
        container.className = 'airport-input-container';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'airport-input';
        input.placeholder = 'Enter city or airport code';
        input.required = true;
        
        const suggestions = document.createElement('div');
        suggestions.className = 'airport-suggestions';
        
        container.appendChild(input);
        container.appendChild(suggestions);
        
        setupAirportAutocomplete(input, suggestions);
        return container;
    }

    function setupAirportAutocomplete(input, suggestions) {
        input.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            if (query.length < 2) {
                suggestions.classList.remove('active');
                return;
            }
            
            const matches = airports.filter(airport => 
                airport.code.toLowerCase().includes(query) ||
                airport.city.toLowerCase().includes(query) ||
                airport.name.toLowerCase().includes(query)
            ).slice(0, 5);
            
            if (matches.length > 0) {
                suggestions.innerHTML = matches.map(airport => `
                    <div class="airport-suggestion" data-code="${airport.code}">
                        ${airport.city} (${airport.code}) - ${airport.name}
                    </div>
                `).join('');
                suggestions.classList.add('active');
                
                suggestions.querySelectorAll('.airport-suggestion').forEach(suggestion => {
                    suggestion.addEventListener('click', function() {
                        const code = this.dataset.code;
                        const airport = airports.find(a => a.code === code);
                        selectAirport(input, airport);
                        suggestions.classList.remove('active');
                    });
                });
            } else {
                suggestions.classList.remove('active');
            }
        });
        
        // Close suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !suggestions.contains(e.target)) {
                suggestions.classList.remove('active');
            }
        });
    }

    function selectAirport(input, airport) {
        if (selectedAirports.some(a => a.code === airport.code)) {
            return;
        }
        
        const container = input.closest('.airport-input-container');
        input.value = '';
        
        const selectedAirport = document.createElement('div');
        selectedAirport.className = 'selected-airport';
        selectedAirport.innerHTML = `
            <span>${airport.city} (${airport.code})</span>
            <i class="fas fa-times remove-airport"></i>
        `;
        
        selectedAirport.querySelector('.remove-airport').addEventListener('click', function() {
            selectedAirports = selectedAirports.filter(a => a.code !== airport.code);
            selectedAirport.remove();
            updateAddAirportButton();
            
            // If no airport inputs exist, add one
            if (document.querySelectorAll('.airport-input').length === 0) {
                departureAirports.insertBefore(createAirportInput(), addAirportBtn);
            }
        });
        
        container.appendChild(selectedAirport);
        selectedAirports.push(airport);
        updateAddAirportButton();
        
        // Remove the input if we have reached the maximum number of airports
        if (selectedAirports.length >= MAX_AIRPORTS) {
            const inputToRemove = container.querySelector('.airport-input');
            if (inputToRemove) {
                inputToRemove.remove();
            }
        }
    }

    function updateAddAirportButton() {
        const hasAvailableInput = document.querySelector('.airport-input') !== null;
        const showButton = selectedAirports.length < MAX_AIRPORTS && !hasAvailableInput;
        addAirportBtn.style.display = showButton ? 'block' : 'none';
    }

    // Initialize first airport input
    const existingInput = document.querySelector('.airport-input');
    if (existingInput) {
        setupAirportAutocomplete(
            existingInput, 
            existingInput.nextElementSibling
        );
    } else {
        departureAirports.insertBefore(createAirportInput(), addAirportBtn);
    }

    // Add airport button handler
    addAirportBtn.addEventListener('click', function() {
        if (selectedAirports.length < MAX_AIRPORTS && !document.querySelector('.airport-input')) {
            departureAirports.insertBefore(createAirportInput(), addAirportBtn);
            updateAddAirportButton();
        }
    });

    tripPlannerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const selectedTypes = Array.from(document.querySelectorAll('input[name="tripType"]:checked'))
            .map(checkbox => checkbox.value);
        
        if (selectedTypes.length === 0) {
            alert('Please select at least one trip type');
            return;
        }
        
        if (selectedAirports.length === 0) {
            alert('Please select at least one departure airport');
            return;
        }

        const tripDuration = document.getElementById('tripDuration');
        const maxFlightHours = document.getElementById('maxFlightHours');
        const directFlightsOnly = document.getElementById('directFlightsOnly');
        const preferences = document.getElementById('preferences');
        
        const data = {
            trip_types: selectedTypes,
            departure_airports: selectedAirports.map(airport => airport.code),
            date_range_start: dateRangeStart.value,
            date_range_end: dateRangeEnd.value,
            trip_duration: tripDuration.value,
            max_flight_hours: maxFlightHours.value,
            direct_flights_only: directFlightsOnly.checked,
            preferences: preferences.value
        };
        
        try {
            const response = await fetch('/api/trip/plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                const result = await response.json();
                displayTripSuggestions(result);
            } else {
                const error = await response.json();
                alert('Error planning trip: ' + error.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error planning trip. Please try again.');
        }
    });

    addPointsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const programSelect = document.getElementById('programSelect');
        const selectedOption = programSelect.options[programSelect.selectedIndex];
        const programName = selectedOption.text;
        const programId = selectedOption.value;
        const pointsBalance = document.getElementById('pointsBalance').value;
        
        console.log('Submitting data:', {
            program_name: programName,
            program_id: programId,
            points_balance: parseInt(pointsBalance)
        });
        
        try {
            const response = await fetch('/api/points/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    program_name: programName,
                    program_id: programId,
                    points_balance: parseInt(pointsBalance)
                })
            });
            
            console.log('Response status:', response.status);
            const responseData = await response.json();
            console.log('Response data:', responseData);
            
            if (response.ok) {
                console.log('Creating card for program:', programName);
                // Add points program card to the grid
                const card = createPointsProgramCard(programName, pointsBalance, programId);
                pointsPrograms.appendChild(card);
                
                // Reset form and close modal
                addPointsForm.reset();
                modal.style.display = 'none';
            } else {
                console.error('Server returned error:', responseData);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    function createPointsProgramCard(programName, balance, programId) {
        const card = document.createElement('div');
        card.className = 'points-card mb-3';
        card.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${programName}</h5>
                    <div class="d-flex align-items-center justify-content-between">
                        <p class="card-text mb-0"><span class="points-balance">${parseInt(balance).toLocaleString()}</span> points</p>
                        <div class="btn-group">
                            <button class="btn btn-primary update-points-btn" data-program-id="${programId}">Update</button>
                            <button class="btn btn-danger delete-program-btn" data-program-id="${programId}">Delete</button>
                        </div>
                    </div>
                    <div class="update-points-form d-none mt-3" id="update-form-${programId}">
                        <div class="input-group">
                            <input type="number" class="form-control" placeholder="New point balance" min="0">
                            <button class="btn btn-success confirm-update" type="button">Save</button>
                            <button class="btn btn-secondary cancel-update" type="button">Cancel</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners for update button
        const updateBtn = card.querySelector('.update-points-btn');
        const deleteBtn = card.querySelector('.delete-program-btn');
        const updateForm = card.querySelector('.update-points-form');
        const confirmBtn = card.querySelector('.confirm-update');
        const cancelBtn = card.querySelector('.cancel-update');
        const pointsInput = card.querySelector('input[type="number"]');

        updateBtn.addEventListener('click', () => {
            updateForm.classList.remove('d-none');
            pointsInput.value = balance;
        });

        cancelBtn.addEventListener('click', () => {
            updateForm.classList.add('d-none');
        });

        confirmBtn.addEventListener('click', async () => {
            const newBalance = pointsInput.value;
            if (!newBalance || newBalance < 0) {
                alert('Please enter a valid point balance');
                return;
            }

            try {
                const response = await fetch('/points/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id: programId,
                        points_balance: parseInt(newBalance)
                    })
                });

                if (response.ok) {
                    const balanceDisplay = card.querySelector('.points-balance');
                    balanceDisplay.textContent = parseInt(newBalance).toLocaleString();
                    updateForm.classList.add('d-none');
                } else {
                    alert('Failed to update points balance');
                }
            } catch (error) {
                console.error('Error updating points:', error);
                alert('Error updating points balance');
            }
        });

        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this program?')) {
                try {
                    const response = await fetch('/points/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            id: programId
                        })
                    });

                    if (response.ok) {
                        card.remove();
                    } else {
                        alert('Failed to delete program');
                    }
                } catch (error) {
                    console.error('Error deleting program:', error);
                    alert('Error deleting program');
                }
            }
        });

        return card;
    }

    async function loadPointsPrograms() {
        try {
            const response = await fetch('/points/list');
            if (response.ok) {
                const data = await response.json();
                const pointsPrograms = document.getElementById('active-programs');
                if (!pointsPrograms) {
                    console.error('Could not find active-programs element');
                    return;
                }
                pointsPrograms.innerHTML = ''; // Clear existing cards
                
                if (data.status === 'success' && data.programs.length > 0) {
                    data.programs.forEach(program => {
                        const card = createPointsProgramCard(
                            program.program_name, 
                            program.points_balance,
                            program.id
                        );
                        pointsPrograms.appendChild(card);
                    });
                } else {
                    pointsPrograms.innerHTML = '<p class="text-muted">No loyalty programs added yet.</p>';
                }
            } else {
                console.error('Failed to load points programs');
            }
        } catch (error) {
            console.error('Error loading points programs:', error);
        }
    }

    function displayTripSuggestions(data) {
        const tripSuggestions = document.getElementById('tripSuggestions');
        const plan = data.trip_plan;
        
        let html = '<div class="suggestions-container">';
        
        // Destinations
        html += '<div class="suggestion-card">';
        html += '<h3>🌍 Recommended Destinations</h3>';
        plan.destinations.forEach(dest => {
            html += `
                <div class="destination-item">
                    <h4>${dest.name}</h4>
                    <p>${dest.rationale}</p>
                    <ul>
                        ${dest.highlights.map(h => `<li>${h}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        html += '</div>';
        
        // Flights
        html += '<div class="suggestion-card">';
        html += '<h3>✈️ Flight Options</h3>';
        plan.flights.options.forEach(flight => {
            html += `
                <div class="flight-item">
                    <p><strong>From:</strong> ${flight.from}</p>
                    <p><strong>Estimated Price:</strong> ${flight.estimated_price}</p>
                    <p><strong>Duration:</strong> ${flight.duration}</p>
                </div>
            `;
        });
        html += '</div>';
        
        // Accommodations
        html += '<div class="suggestion-card">';
        html += '<h3>🏨 Where to Stay</h3>';
        plan.accommodations.forEach(acc => {
            html += `
                <div class="accommodation-item">
                    <h4>${acc.name}</h4>
                    <p><strong>Type:</strong> ${acc.type}</p>
                    <p><strong>Price Range:</strong> ${acc.price_range}</p>
                    <ul>
                        ${acc.highlights.map(h => `<li>${h}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        html += '</div>';
        
        // Itinerary
        html += '<div class="suggestion-card">';
        html += '<h3>📅 Suggested Itinerary</h3>';
        Object.entries(plan.itinerary).forEach(([day, activities]) => {
            html += `
                <div class="itinerary-day">
                    <h4>${day.charAt(0).toUpperCase() + day.slice(1)}</h4>
                    <p><strong>Morning:</strong> ${activities.morning}</p>
                    <p><strong>Afternoon:</strong> ${activities.afternoon}</p>
                    <p><strong>Evening:</strong> ${activities.evening}</p>
                </div>
            `;
        });
        html += '</div>';
        
        // Budget
        html += '<div class="suggestion-card">';
        html += '<h3>💰 Estimated Budget</h3>';
        html += `
            <div class="budget-breakdown">
                <p><strong>Flights:</strong> $${plan.estimated_budget.flights}</p>
                <p><strong>Accommodations:</strong> $${plan.estimated_budget.accommodations}</p>
                <p><strong>Activities:</strong> $${plan.estimated_budget.activities}</p>
                <p class="total-budget"><strong>Total:</strong> $${plan.estimated_budget.total}</p>
            </div>
        `;
        html += '</div>';
        
        // Weather and Events
        html += '<div class="suggestion-card">';
        html += `
            <h3>🌤️ Weather & Events</h3>
            <p><strong>Weather Forecast:</strong> ${plan.weather_forecast}</p>
            <div class="events-list">
                <h4>Special Events During Your Stay</h4>
                ${plan.events.map(event => `
                    <div class="event-item">
                        <h5>${event.name}</h5>
                        <p><strong>When:</strong> ${event.date}</p>
                        <p>${event.description}</p>
                    </div>
                `).join('')}
            </div>
        `;
        html += '</div>';
        
        html += '</div>';
        tripSuggestions.innerHTML = html;
        tripSuggestions.scrollIntoView({ behavior: 'smooth' });
    }

});

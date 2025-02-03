/**
 * Departing Airports Module
 * Handles airport search and selection functionality
 */
const DepartingAirports = {
    initialized: false,
    doneTypingInterval: 300,
    typingTimers: {},

    init() {
        if (this.initialized) {
            console.warn('DepartingAirports module already initialized');
            return;
        }
        console.log('Initializing DepartingAirports module');

        if (typeof airports === 'undefined') {
            console.error('Airports data not loaded!');
            return;
        }

        this.setupAirportInputs();
        this.initialized = true;
        console.log('DepartingAirports module initialized');
    },

    setupAirportInputs() {
        const airportInputs = document.querySelectorAll('.airport-input');
        console.log('Setting up', airportInputs.length, 'airport inputs');

        airportInputs.forEach((input, index) => {
            console.log(`Setting up airport input ${index}`);
            
            const inputGroup = input.closest('.airport-input-group');
            const suggestionsContainer = inputGroup.querySelector('.airport-suggestions');

            input.addEventListener('input', () => this.handleAirportInput(input, suggestionsContainer, index));
            
            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                    suggestionsContainer.style.display = 'none';
                }
            });
        });
    },

    handleAirportInput(input, suggestionsContainer, index) {
        clearTimeout(this.typingTimers[index]);
        const query = input.value.toUpperCase();
        console.log(`Airport search query for input ${index}:`, query);

        this.typingTimers[index] = setTimeout(() => {
            if (query.length >= 2) {
                const matchingAirports = this.searchAirports(query);
                this.displayAirportSuggestions(matchingAirports, input, suggestionsContainer);
            } else {
                suggestionsContainer.style.display = 'none';
            }
        }, this.doneTypingInterval);
    },

    searchAirports(query) {
        console.log('Searching airports for:', query);
        return airports.filter(airport => 
            airport.code.includes(query) || 
            airport.city.toUpperCase().includes(query) ||
            airport.name.toUpperCase().includes(query)
        ).slice(0, 10);
    },

    displayAirportSuggestions(matchingAirports, input, suggestionsContainer) {
        console.log('Displaying', matchingAirports.length, 'airport suggestions');
        
        suggestionsContainer.innerHTML = '';
        matchingAirports.forEach(airport => {
            const div = document.createElement('div');
            div.className = 'suggestion';
            div.textContent = `${airport.code} - ${airport.name}, ${airport.city}`;
            
            div.addEventListener('click', () => {
                input.value = `${airport.code} - ${airport.name}, ${airport.city}`;
                const hiddenInput = input.closest('.airport-input-group').querySelector('.airport-code');
                if (hiddenInput) {
                    hiddenInput.value = airport.code;
                }
                suggestionsContainer.style.display = 'none';
            });
            
            suggestionsContainer.appendChild(div);
        });

        suggestionsContainer.style.display = matchingAirports.length > 0 ? 'block' : 'none';
    },

    getSelectedAirports() {
        return Array.from(document.querySelectorAll('.airport-code'))
            .map(input => input.value.trim())
            .filter(code => code);
    }
};

// Export the module
window.DepartingAirports = DepartingAirports;

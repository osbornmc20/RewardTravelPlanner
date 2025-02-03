/**
 * Trip Generator Module
 * Handles trip generation and results display
 */
const TripGenerator = {
    initialized: false,
    generateButton: null,
    resultsContainer: null,

    init() {
        if (this.initialized) {
            console.warn('TripGenerator module already initialized');
            return;
        }
        console.log('Initializing TripGenerator module');

        this.generateButton = document.getElementById('generateTripIdeas');
        this.resultsContainer = document.getElementById('trip-results');

        if (!this.generateButton || !this.resultsContainer) {
            console.error('Required elements not found:', {
                generateButton: !!this.generateButton,
                resultsContainer: !!this.resultsContainer
            });
            return;
        }

        this.generateButton.addEventListener('click', this.generateTrip.bind(this));
        this.initialized = true;
        console.log('TripGenerator module initialized');
    },

    async generateTrip() {
        console.log('Generate trip button clicked');
        this.clearResults();

        try {
            // Validate required fields
            const errors = TripInfo.validateTripInfo();
            const airports = DepartingAirports.getSelectedAirports();
            const tripTypes = TripTypes.getSelectedTypes();
            
            if (!airports || !airports.length) {
                errors.push('At least one departure airport is required');
            }
            if (!tripTypes || !tripTypes.length) {
                errors.push('At least one trip type is required');
            }

            if (errors.length > 0) {
                this.displayErrors(errors);
                return;
            }

            this.setGeneratingState(true);
            
            // Collect and validate data from all modules
            const tripInfo = TripInfo.getTripInfo();
            const tripData = {
                trip_types: tripTypes,
                airports: airports,
                ...tripInfo
            };

            // Additional validation before sending
            if (!tripData.trip_length || !tripData.max_flight_length) {
                throw new Error('Trip length and maximum flight length are required');
            }

            console.log('Sending trip data:', tripData);
            
            const response = await this.sendTripRequest(tripData);
            await this.handleTripResponse(response);
        } catch (error) {
            console.error('Error generating trip:', error);
            this.displayError(error.message || 'An unexpected error occurred. Please try again.');
        } finally {
            this.setGeneratingState(false);
        }
    },

    async sendTripRequest(tripData) {
        const response = await fetch('/generate_trip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tripData)
        });

        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        // Clone response before reading
        const responseClone = response.clone();
        
        try {
            const data = await response.json();
            console.log('Response data:', data);
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Failed to generate trip');
            }
            
            return data;
        } catch (jsonError) {
            console.error('JSON parsing error:', jsonError);
            const text = await responseClone.text();
            console.error('Response text:', text);
            throw new Error('Error generating trip. Please try again.');
        }
    },

    clearResults() {
        this.resultsContainer.innerHTML = '';
    },

    displayErrors(errors) {
        this.resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <strong>Please fix the following errors:</strong>
                <ul>
                    ${errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
    },

    displayError(error) {
        this.resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${error}
            </div>
        `;
    },

    setGeneratingState(isGenerating) {
        this.generateButton.disabled = isGenerating;
        this.generateButton.innerHTML = isGenerating ? 
            '<i class="fas fa-spinner fa-spin me-2"></i>Generating...' : 
            'Generate Trip Ideas';
    },

    async handleTripResponse(data) {
        console.log('Handling trip response:', data);
        
        if (!data.result) {
            throw new Error('No trip results received');
        }

        // Split the response into destinations and filter out empty ones
        const destinations = data.result
            .split(/DESTINATION \d+ -/)
            .filter(d => d.trim())
            .map(d => d.trim());
        
        // Create the HTML for each destination
        let resultsHtml = '<div class="trip-results-container">';
        
        destinations.forEach((destination, index) => {
            // Extract destination header and preference match
            const lines = destination.split('\n').map(l => l.trim()).filter(l => l);
            const destName = lines[0].replace(':', '').trim();
            
            // Skip if we don't have enough content
            if (lines.length < 5) {
                console.error('Incomplete destination data:', destination);
                return;
            }
            
            let prefMatch = '';
            let content = destination;
            
            // Find preference match section
            const prefMatchIndex = lines.findIndex(l => l.startsWith('Preference Match:'));
            if (prefMatchIndex !== -1) {
                prefMatch = lines[prefMatchIndex].replace('Preference Match:', '').trim();
                content = lines.slice(prefMatchIndex + 1).join('\n');
            }

            // Split into economy and luxury options
            const [economySection = '', luxurySection = ''] = content.split(/OPTION B - LUXURY EXPERIENCE/i);
            
            // Only create the destination section if we have valid data
            if (economySection && luxurySection && destName !== 'Unknown Destination') {
                resultsHtml += `
                    <div class="destination-section mb-5">
                        <h2 class="destination-header mb-3">Destination ${index + 1} - ${destName}</h2>
                        <div class="preference-match mb-3">
                            <strong>Preference Match:</strong> ${prefMatch}
                        </div>
                        
                        <div class="row">
                            <!-- Economy Column -->
                            <div class="col-md-6">
                                <div class="option-section">
                                    <h3 class="option-header">Economy Experience</h3>
                                    ${this.formatOptionSection(economySection)}
                                </div>
                            </div>
                            
                            <!-- Luxury Column -->
                            <div class="col-md-6">
                                <div class="option-section">
                                    <h3 class="option-header">Luxury Experience</h3>
                                    ${this.formatOptionSection(luxurySection)}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        if (!resultsHtml.includes('destination-section')) {
            resultsHtml += `
                <div class="alert alert-danger">
                    Unable to generate valid trip suggestions. Please try again.
                </div>
            `;
        }
        
        resultsHtml += '</div>';
        this.resultsContainer.innerHTML = resultsHtml;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .trip-results-container {
                padding: 20px;
            }
            .destination-header {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .preference-match {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .option-section {
                margin-bottom: 20px;
            }
            .option-header {
                color: #2c3e50;
                font-size: 1.5rem;
                margin-bottom: 15px;
            }
            .detail-box {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .detail-box h4 {
                color: #3498db;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            .detail-box ul {
                list-style: none;
                padding-left: 0;
                margin-bottom: 0;
            }
            .detail-box li {
                margin-bottom: 5px;
                padding-left: 20px;
                position: relative;
            }
            .detail-box li:before {
                content: "•";
                position: absolute;
                left: 0;
                color: #3498db;
            }
            .detail-box li.indented {
                padding-left: 40px;
            }
            .detail-box li.indented:before {
                left: 20px;
            }
        `;
        document.head.appendChild(style);
    },

    formatOptionSection(section) {
        if (!section) return '';
        
        const lines = section.trim().split('\n');
        let html = '<div class="option-content">';
        
        // Flight Details Box
        let flightDetails = '';
        let hotelOption = '';
        let valueAnalysis = '';
        let currentSection = '';
        
        // Helper function to clean and validate content
        const isValidContent = (content) => {
            if (!content) return false;
            const cleaned = content.trim();
            return cleaned && cleaned !== '-' && cleaned !== '--' && cleaned !== '•';
        };
        
        lines.forEach(line => {
            line = line.trim();
            if (!line || line === '-' || line === '--' || line === '•') return;
            
            if (line.includes('Flight Details:')) {
                currentSection = 'flight';
            } else if (line.includes('Hotel Option:')) {
                currentSection = 'hotel';
            } else if (line.includes('Value Analysis:')) {
                currentSection = 'value';
            } else if (line.startsWith('-') || line.startsWith('*')) {
                const content = line.substring(1).trim();
                if (!isValidContent(content)) return;
                
                const isIndented = line.startsWith('*');
                const className = isIndented ? 'indented' : '';
                
                switch (currentSection) {
                    case 'flight':
                        flightDetails += `<li>${content}</li>`;
                        break;
                    case 'hotel':
                        hotelOption += `<li>${content}</li>`;
                        break;
                    case 'value':
                        valueAnalysis += `<li class="${className}">${content}</li>`;
                        break;
                }
            }
        });
        
        // Only add sections that have content
        let sectionsHtml = '';
        
        if (flightDetails) {
            sectionsHtml += `
                <div class="detail-box">
                    <h4>Flight Details</h4>
                    <ul>${flightDetails}</ul>
                </div>
            `;
        }
        
        if (hotelOption) {
            sectionsHtml += `
                <div class="detail-box">
                    <h4>Hotel Option</h4>
                    <ul>${hotelOption}</ul>
                </div>
            `;
        }
        
        if (valueAnalysis) {
            sectionsHtml += `
                <div class="detail-box">
                    <h4>Value Analysis</h4>
                    <ul>${valueAnalysis}</ul>
                </div>
            `;
        }
        
        return html + sectionsHtml + '</div>';
    },

    formatExperience(text) {
        if (!text) return '';
        
        // Split into sentences
        const sentences = text.split(/(?<=[.!?])\s+/);
        
        // Format each sentence
        return sentences.map(sentence => {
            // Highlight key phrases
            sentence = sentence
                .replace(/(\d+(?:\.\d+)?%)/g, '<span class="highlight-stat">$1</span>')
                .replace(/(\$\d+(?:,\d{3})*(?:\.\d{2})?)/g, '<span class="highlight-price">$1</span>')
                .replace(/(\d+ (?:hour|minute|day|week|month|year)s?)/gi, '<span class="highlight-time">$1</span>');
            
            return sentence;
        }).join(' ');
    }
};

// Export the module
window.TripGenerator = TripGenerator;

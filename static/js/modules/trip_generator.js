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
        console.log('Generating trip...');
        
        try {
            // Get trip types
            const tripTypes = window.TripTypes.getSelectedTypes();
            if (!tripTypes || tripTypes.length === 0) {
                throw new Error('Please select at least one trip type');
            }
            
            // Get airports
            const airports = window.DepartingAirports.getSelectedAirports();
            if (!airports || airports.length === 0) {
                throw new Error('Please select at least one departure airport');
            }
            
            // Get trip info
            const tripInfo = window.TripInfo.getTripInfo();
            const tripErrors = window.TripInfo.validateTripInfo();
            if (tripErrors.length > 0) {
                throw new Error(tripErrors.join('\n'));
            }

            // Get points programs from active programs
            const pointsPrograms = $('.points-input').map(function() {
                const $card = $(this).closest('.card');
                return {
                    program_name: $card.find('.card-title').text().trim(),
                    points_balance: parseInt($(this).val())
                };
            }).get();

            if (pointsPrograms.length === 0) {
                throw new Error('Please add at least one loyalty program to get personalized trip recommendations');
            }
            
            // Combine all data
            const tripData = {
                trip_types: tripTypes,
                airports: airports,
                points_programs: pointsPrograms,
                ...tripInfo
            };
            
            console.log('Sending trip request with data:', tripData);
            
            // Show loading state
            this.setGeneratingState(true);
            this.clearResults();
            
            // Send request
            const data = await this.sendTripRequest(tripData);
            await this.handleTripResponse(data);
            
        } catch (error) {
            console.error('Error generating trip:', error);
            this.displayError(error.message || 'An unexpected error occurred. Please try again - it usually works on the second try!');
        } finally {
            this.setGeneratingState(false);
        }
    },

    async sendTripRequest(tripData) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

        try {
            const response = await fetch('/generate_trip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(tripData),
                signal: controller.signal
            });

            // Clone the response for potential error handling
            const responseClone = response.clone();

            // First check if response is ok
            if (!response.ok) {
                // For non-200 responses, try to get error details
                try {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'A temporary error occurred. Please try your request again - it usually works on the second try!');
                } catch (jsonError) {
                    // If we can't parse JSON, use the cloned response to get text
                    const text = await responseClone.text();
                    // Check if it's an HTML response (indicating a server error)
                    if (text.includes('<!DOCTYPE html>')) {
                        throw new Error('A temporary server hiccup occurred. Please try again - it usually works on the second try!');
                    }
                    throw new Error('A temporary error occurred. Please try your request again - it usually works on the second try!');
                }
            }

            // For 200 responses, try to parse JSON
            try {
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.error || 'A temporary error occurred. Please try your request again - it usually works on the second try!');
                }
                return data;
            } catch (jsonError) {
                console.error('JSON parsing error:', jsonError);
                throw new Error('A temporary error occurred while processing the response. Please try again - it usually works on the second try!');
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('The request took longer than expected. Please try again - it usually works on the second try!');
            }
            throw error;
        } finally {
            clearTimeout(timeoutId);
        }
    },

    clearResults() {
        this.resultsContainer.innerHTML = '';
    },

    displayError(message) {
        const errorHtml = `
            <div class="alert alert-danger" role="alert">
                ${message}
            </div>
        `;
        this.resultsContainer.innerHTML = errorHtml;
    },

    setGeneratingState(isGenerating) {
        const button = this.generateButton;
        const spinner = button.querySelector('.spinner-border');
        
        if (isGenerating) {
            button.disabled = true;
            spinner.classList.remove('d-none');
            button.innerHTML = `
                Marshall Is Thinking...
                <div class="spinner-border spinner-border-sm ms-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
        } else {
            button.disabled = false;
            spinner.classList.add('d-none');
            button.innerHTML = `
                Ask Marshall
                <div class="spinner-border spinner-border-sm ms-2 d-none" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
        }
    },

    async handleTripResponse(data) {
        // Add essential styles
        const style = document.createElement('style');
        style.textContent = `
            .trip-results-container {
                padding: 20px;
            }
            .destination-section {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .destination-header {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            .destination-summary {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
                margin-bottom: 20px;
            }
            .option-section {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .option-header {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }
        `;
        document.head.appendChild(style);
        console.log('Handling trip response:', data);

        if (!data || !data.success || !data.result) {
            throw new Error('No trip recommendations were received. Please try again - it usually works on the second try!');
        }

        // Split the response into destinations and filter out empty ones
        const destinations = data.result
            .split(/DESTINATION \d+ -/)
            .filter(d => d.trim())
            .map(d => d.trim());
        
        // Create the HTML for each destination
        let resultsHtml = '<div class="trip-results-container">';
        
        destinations.forEach((destination, index) => {
            // Extract destination header and summary sections
            const lines = destination.split('\n').map(l => l.trim()).filter(l => l);
            const destName = lines[0].replace(':', '').trim();
            
            // Skip if we don't have enough content
            if (lines.length < 5) {
                console.error('Incomplete destination data:', destination);
                return;
            }
            
            // Find destination summary and recommendations sections
            const summaryStartIndex = lines.findIndex(l => l === 'DESTINATION SUMMARY:');
            const recommendationsStartIndex = lines.findIndex(l => l === 'Why We Recommend This Destination:');
            const optionsStartIndex = lines.findIndex(l => l.includes('OPTION A - ECONOMY EXPERIENCE'));
            
            let destinationSummary = '';
            let recommendations = '';
            let content = destination;
            
            if (summaryStartIndex !== -1 && recommendationsStartIndex !== -1) {
                // Extract summary
                destinationSummary = lines
                    .slice(summaryStartIndex + 1, recommendationsStartIndex)
                    .filter(l => l)
                    .join('<br>');
                
                // Extract recommendations
                recommendations = lines
                    .slice(recommendationsStartIndex + 1, optionsStartIndex)
                    .filter(l => l)
                    .join('<br>');
                
                // Get the rest of the content
                content = lines.slice(optionsStartIndex).join('\n');
            }
            
            // Split into economy and luxury options
            const [economySection = '', luxurySection = ''] = content.split(/OPTION B - LUXURY EXPERIENCE/i);
            
            // Only create the destination section if we have valid data
            if (economySection && luxurySection && destName !== 'Unknown Destination') {
                resultsHtml += `
                    <div class="destination-section mb-5">
                        <h2 class="destination-header mb-4">Destination ${index + 1} - ${destName}</h2>
                        
                        <div class="destination-summary mb-4">
                            <div class="summary-section mb-4">
                                <h4 class="summary-title">Overview</h4>
                                <div class="summary-content">
                                    ${destinationSummary}
                                </div>
                            </div>
                            
                            <div class="recommendations-section">
                                <h4 class="summary-title">Why We Recommend This Destination</h4>
                                <div class="recommendations-content">
                                    ${recommendations.split('<br>').map(rec => {
                                        // Check if it's a main section header (ends with ':')
                                        if (rec.endsWith(':')) {
                                            return `<h5 class="recommendation-category">${rec}</h5>`;
                                        }
                                        // Check if it's a bullet point
                                        else if (rec.startsWith('-')) {
                                            return `<div class="recommendation-item">${rec.substring(1)}</div>`;
                                        }
                                        return rec;
                                    }).join('')}
                                </div>
                            </div>
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
                    Unable to generate valid trip suggestions. Please try again - it usually works on the second try!
                </div>
            `;
        }
        
        resultsHtml += '</div>';
        this.resultsContainer.innerHTML = resultsHtml;
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

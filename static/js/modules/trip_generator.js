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
        // Increase timeout to 2 minutes if there are multiple special requests
        const hasMultipleRequests = tripData.preferences && tripData.preferences.split('\n').length > 1;
        const timeout = hasMultipleRequests ? 180000 : 120000;  // 3 minutes for multiple requests, 2 minutes for single
        const timeoutId = setTimeout(() => controller.abort(), timeout);

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
            const summaryStartIndex = lines.findIndex(l => l === 'DESTINATION SUMMARY:' || l === 'Overview:');
            const recommendationsStartIndex = lines.findIndex(l => l === 'Why We Recommend This Destination:');
            const optionsStartIndex = lines.findIndex(l => l.includes('OPTION A - ECONOMY EXPERIENCE') || l === 'Economy Experience:');
            
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
            const luxuryStart = content.includes('OPTION B - LUXURY EXPERIENCE') ? 
                content.indexOf('OPTION B - LUXURY EXPERIENCE') : 
                content.indexOf('Luxury Experience:');
            
            const economySection = content.substring(0, luxuryStart).trim();
            const luxurySection = content.substring(luxuryStart).trim();
            
            // Only create the destination section if we have valid data
            if (economySection && luxurySection && destName !== 'Unknown Destination') {
                resultsHtml += `
                    <section class="destination-section">
                        <div class="destination-header" onclick="this.classList.toggle('active'); this.nextElementSibling.classList.toggle('show');">
                            <h3>Destination ${index + 1} - ${destName}</h3>
                            <span class="toggle-icon">▼</span>
                        </div>
                        <div class="destination-content${window.innerWidth <= 768 ? '' : ' show'} mobile-full-width">
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
                    </section>
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
        
        // Dispatch event when results are loaded
        document.dispatchEvent(new Event('tripResultsLoaded'));

        // Add click handlers for Continue Planning buttons
        document.querySelectorAll('.select-trip-option').forEach(button => {
            button.addEventListener('click', (e) => {
                // Remove selection from other options
                document.querySelectorAll('.option-content').forEach(content => {
                    content.classList.remove('selected');
                });
                
                // Add selection to clicked option
                const optionContent = e.target.closest('.option-content');
                optionContent.classList.add('selected');
                
                // Hide default state and show selected state
                document.querySelector('.default-state').style.display = 'none';
                document.querySelector('.selected-trip-summary').style.display = 'block';
                
                console.log('Continue Planning button clicked');
                
                // Get trip details from the selected option
                const optionType = button.dataset.optionType;
                const destinationSection = optionContent.closest('.destination-section');
                
                // Extract destination from the destination header
                const destinationHeader = destinationSection.querySelector('.destination-header h3');
                let destination = destinationHeader.textContent.replace(/Destination \d+ - /, '').trim();
                
                // Extract hotel and route from the content
                let hotel = 'Selected Hotel';
                let route = null;
                
                // Look for hotel info and route in all list items
                const allListItems = optionContent.querySelectorAll('li');
                allListItems.forEach(item => {
                    const text = item.textContent.trim();
                    
                    // Extract hotel name from Property field
                    if (text.startsWith('Property:')) {
                        hotel = text.split('Property:')[1].trim();
                    }
                    
                    // Extract route
                    if (text.startsWith('Route:')) {
                        route = text.split('Route:')[1].split('(')[0].trim();
                    }
                });
                
                // If we found a route, use it as the destination
                if (route) {
                    destination = route;
                }
                
                // Log what we found for debugging
                console.log('Found trip details:', {
                    destinationHeader: destinationHeader?.textContent,
                    destination,
                    hotel,
                    route,
                    optionType,
                    allListItems: Array.from(allListItems).map(li => li.textContent)
                });

                // Get trip month and length
                const tripMonth = document.querySelector('#travelMonths')?.value;
                const tripLength = document.querySelector('#tripLength')?.value;
                
                // Log the extracted details for debugging
                console.log('Extracted trip details:', {
                    destination,
                    hotel,
                    tripMonth,
                    tripLength,
                    optionType
                });

                // Update trip summary
                const tripSummary = document.querySelector('.selected-trip-summary');
                if (tripSummary) {
                    // Get the correct option type from the section header
                    const optionSection = optionContent.closest('.option-section');
                    const optionHeader = optionSection?.querySelector('.option-header');
                    const isLuxury = optionHeader?.textContent.includes('Luxury');
                    
                    tripSummary.innerHTML = `
                        <div class="selected-option-details">
                            <h4>Selected Option:</h4>
                            <p><strong>${isLuxury ? 'Luxury' : 'Economy'} Experience</strong></p>
                            <p><strong>Route:</strong> ${destination}</p>
                            <p><strong>Hotel:</strong> ${hotel}</p>
                            <p><strong>Travel Month:</strong> ${tripMonth || ''}</p>
                            <p><strong>Duration:</strong> ${tripLength ? `${tripLength} days` : ''}</p>
                        </div>
                        <div class="mindtrip-button-container text-center mt-4">
                            <button id="mindtrip-btn" class="btn btn-primary">
                                <i class="fas fa-plane-departure"></i> Continue Planning on MindTrip.ai
                            </button>
                        </div>
                    `;
                    
                    // Re-attach click handler for MindTrip button
                    const mindTripBtn = document.getElementById('mindtrip-btn');
                    if (mindTripBtn) {
                        mindTripBtn.addEventListener('click', async () => {
                            // Create the prompt
                            const prompt = `I'm planning a ${tripLength}-day ${isLuxury ? 'luxury' : 'budget-friendly'} trip to ${destination} in ${tripMonth}, staying at ${hotel}. Please help me create a detailed day-by-day itinerary that includes:

1. Activities and attractions that match the ${isLuxury ? 'luxury' : 'budget-conscious'} nature of my trip
2. Restaurant recommendations for each day
3. Transportation suggestions
4. Any specific tips for my hotel area
5. Estimated timing for each activity

Please organize this by day (Day 1, Day 2, etc) and consider the local weather and best times for each activity.`;
                            
                            try {
                                // Copy to clipboard
                                await navigator.clipboard.writeText(prompt);
                                
                                // Create and show notification
                                const notification = document.createElement('div');
                                notification.className = 'alert alert-success position-fixed';
                                notification.style.cssText = `
                                    position: fixed;
                                    bottom: 20px;
                                    right: 20px;
                                    z-index: 1000;
                                    padding: 15px 25px;
                                    border-radius: 5px;
                                    background-color: #28a745;
                                    color: white;
                                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                                    display: flex;
                                    align-items: center;
                                    gap: 10px;
                                    font-weight: 500;
                                `;
                                notification.innerHTML = `
                                    <i class="fas fa-check-circle" style="font-size: 1.2em;"></i>
                                    Trip Plan copied, opening MindTrip
                                `;
                                
                                document.body.appendChild(notification);
                                
                                // Remove notification after 3 seconds
                                setTimeout(() => {
                                    notification.remove();
                                    // Open MindTrip in a new tab
                                    window.open('https://mindtrip.ai/chat', '_blank');
                                }, 3000);
                                
                            } catch (error) {
                                console.error('Error handling MindTrip integration:', error);
                                // Show error notification
                                const errorNotification = document.createElement('div');
                                errorNotification.className = 'alert alert-danger position-fixed';
                                errorNotification.style.bottom = '20px';
                                errorNotification.style.right = '20px';
                                errorNotification.style.zIndex = '1000';
                                errorNotification.innerHTML = 'Error copying trip details';
                                document.body.appendChild(errorNotification);
                                setTimeout(() => errorNotification.remove(), 3000);
                            }
                        });
                    }
                }
                
                // Scroll to trip summary
                tripSummary?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });
    },

    formatOptionSection(section) {
        if (!section) return '';
        
        const lines = section.trim().split('\n');
        let html = '<div class="option-content" data-trip-details="">';
        
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

        // Helper function to format content with bold keywords
        const formatContent = (content) => {
            // Replace 'round trip' with 'RT'
            content = content.replace(/round trip/gi, 'RT');
            
            // Format fare type to be in parentheses at the end of points used
            if (content.includes('Fare Type:')) {
                return '';
            }
            if (content.includes('Points used:')) {
                const fareType = lines.find(l => l.includes('Fare Type:'));
                if (fareType) {
                    const type = fareType.split(':')[1].trim();
                    content = content.replace('Points used:', 'Points used') + ` (${type})`;
                }
            }

            // Skip Award Availability lines
            if (content.includes('Award Availability:')) {
                return '';
            }

            // Bold key elements
            const keywords = [
                'Route:', 'Airline:', 'Points Program:', 'Hotel:', 
                'Points Used:', 'Total Points Needed:', 'Property:', 'Property Details:',
                'Points Breakdown:', 'Dollar Value Saved:', 'Cash value:', 'Points value:'
            ];
            keywords.forEach(keyword => {
                content = content.replace(keyword, `<strong>${keyword}</strong>`);
            });

            return content;
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
                
                const isIndented = line.startsWith('*') || 
                                  (currentSection === 'value' && 
                                   (content.includes('Airline:') || content.includes('Hotel:')));
                const className = isIndented ? 'indented' : '';
                
                const formattedContent = formatContent(content);
                if (!formattedContent) return;

                switch (currentSection) {
                    case 'flight':
                        flightDetails += `<li class="${className}">${formattedContent}</li>`;
                        break;
                    case 'hotel':
                        hotelOption += `<li class="${className}">${formattedContent}</li>`;
                        break;
                    case 'value':
                        valueAnalysis += `<li class="${className}">${formattedContent}</li>`;
                        break;
                }
            }
        });
        
        // Only add sections that have content
        let sectionsHtml = '';
        
        if (flightDetails) {
            sectionsHtml += `
                <div class="detail-section mobile-full-width">
                    <h4 class="section-title">Flight Details</h4>
                    <div class="detail-content">
                        <ul>${flightDetails}</ul>
                    </div>
                </div>
            `;
        }
        
        if (hotelOption) {
            sectionsHtml += `
                <div class="detail-section mobile-full-width">
                    <h4 class="section-title">Hotel Option</h4>
                    <div class="detail-content">
                        <ul>${hotelOption}</ul>
                    </div>
                </div>
            `;
        }
        
        if (valueAnalysis) {
            sectionsHtml += `
                <div class="detail-section mobile-full-width">
                    <h4 class="section-title">Value Analysis</h4>
                    <div class="detail-content">
                        <ul>${valueAnalysis}</ul>
                    </div>
                </div>
            `;
        }

        // Add selection button
        sectionsHtml += `
            <div class="text-center mt-4">
                <button class="btn btn-outline-primary select-trip-option" data-option-type="${section.includes('Luxury') ? 'luxury' : 'economy'}">
                    <i class="fas fa-plane-departure me-2"></i>Continue Planning
                </button>
            </div>
        `;
        
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

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
                display: flex;
                justify-content: space-between;
                align-items: center;
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
            .mindtrip-guide {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                height: 100%;
                margin-bottom: 1rem;
            }
            .steps-container {
                padding: 10px;
            }
            .step {
                display: flex;
                align-items: start;
                gap: 15px;
                padding: 10px;
                border-radius: 6px;
                transition: all 0.3s ease;
            }
            .step:hover {
                background-color: #e9ecef;
            }
            .step-number {
                background-color: #3498db;
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                flex-shrink: 0;
            }
            .step-content {
                flex-grow: 1;
            }
            .mindtrip-btn {
                padding: 12px 24px;
                font-size: 1.1rem;
                transition: all 0.3s ease;
            }
            .mindtrip-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
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
        let resultsHtml = '<div class="trip-results-container" style="width:100%; max-width:100%;">';
        
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
            
            // Process economy and luxury sections
            const sections = this.processSectionContent(content, index + 1);
            
            // Only create the destination section if we have valid data
            if (sections.economyContent && sections.luxuryContent && destName !== 'Unknown Destination') {
                resultsHtml += `
                    <section class="destination-section">
                        <div class="destination-header${window.innerWidth <= 768 ? '' : ' active'}">
                            <h3>Destination ${index + 1} - ${destName}</h3>
                            <span class="toggle-icon" style="${window.innerWidth <= 768 ? '' : 'transform: rotate(180deg)'}">▼</span>
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
                                        ${this.formatRecommendations(recommendations)}
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <h2 class="option-header">Economy Experience</h2>
                                    ${this.formatOptionSection(sections.economyContent)}
                                </div>
                                <div class="col-md-6">
                                    <h2 class="option-header">Luxury Experience</h2>
                                    ${this.formatOptionSection(sections.luxuryContent)}
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
        
        // Attach toggle listeners for destination headers
        this.attachToggleListeners();
        console.log('Toggle listeners attached after results HTML loaded');
        
        // Set initial state for destination headers (expanded by default on desktop)
        if (window.innerWidth > 768) {
            document.querySelectorAll('.destination-header').forEach(header => {
                header.classList.add('active');
                
                // Make sure content is visible
                const content = header.nextElementSibling;
                if (content) {
                    content.classList.add('show');
                }
                
                // Rotate toggle icon
                const toggleIcon = header.querySelector('.toggle-icon');
                if (toggleIcon) {
                    toggleIcon.style.transform = 'rotate(180deg)';
                }
            });
        }
        
        // Attach toggle listeners for destination headers
        this.attachToggleListeners();
        
        // Dispatch event when results are loaded
        document.dispatchEvent(new Event('tripResultsLoaded'));

        // Update the Select buttons
        document.querySelectorAll('.select-trip-option').forEach(btn => {
            btn.classList.add('continue-planning-btn');
            // Only remove styling classes, keep the select-trip-option class for reference
            btn.classList.remove('btn', 'btn-outline-primary');
        });

        // Add click handlers for Continue Planning buttons
        document.querySelectorAll('.continue-planning-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Continue Planning clicked');
                
                // Clear any existing selections
                document.querySelectorAll('.option-content, .option-section').forEach(element => {
                    element.classList.remove('selected');
                });
                
                // Find the parent option content and section and add the selected class to both
                const optionContent = e.target.closest('.option-content');
                const optionSection = e.target.closest('.option-section');
                
                if (optionContent) {
                    optionContent.classList.add('selected');
                    console.log('Added selected class to content:', optionContent);
                }
                
                if (optionSection) {
                    optionSection.classList.add('selected');
                    console.log('Added selected class to section:', optionSection);
                }
                
                // Get the option type from the button's data attribute
                const button = e.target.closest('.continue-planning-btn');
                if (button) {
                    const optionType = button.dataset.optionType;
                    window.selectedOption = optionType;
                    console.log('Selected option type:', optionType);
                    
                    // Update the MindTrip banner with the correct experience type
                    const tripSummary = document.querySelector('.trip-summary');
                    if (tripSummary) {
                        // Get existing trip details
                        const destination = tripSummary.querySelector('p:nth-child(1)')?.textContent.split(':')[1]?.trim() || '';
                        const hotel = tripSummary.querySelector('p:nth-child(2)')?.textContent.split(':')[1]?.trim() || '';
                        const month = tripSummary.querySelector('p:nth-child(3)')?.textContent.split(':')[1]?.trim() || '';
                        const duration = tripSummary.querySelector('p:nth-child(4)')?.textContent.split(':')[1]?.trim() || '';
                        
                        // Update the badge and trip summary with the correct experience type
                        tripSummary.innerHTML = `
                            <div class="mb-2">
                                <span class="badge ${optionType === 'luxury' ? 'bg-warning text-dark' : 'bg-info'} mb-2">
                                    ${optionType === 'luxury' ? 'Luxury' : 'Economy'} Experience
                                </span>
                            </div>
                            <div class="text-start">
                                <p class="mb-2"><strong>Route:</strong> ${destination}</p>
                                <p class="mb-2"><strong>Hotel:</strong> ${hotel}</p>
                                <p class="mb-2"><strong>Travel Month:</strong> ${month}</p>
                                <p class="mb-0"><strong>Duration:</strong> ${duration}</p>
                            </div>
                        `;
                    }
                }
                
                const defaultState = document.querySelector('.default-state');
                const selectedTripSummary = document.querySelector('.selected-trip-summary');
                
                if (defaultState) defaultState.style.display = 'none';
                if (selectedTripSummary) selectedTripSummary.style.display = 'block';
                
                console.log('Continue Planning button clicked');
                
                const optionType = button.dataset.optionType;
                const destinationSection = button.closest('.destination-section');
                
                const destinationHeader = destinationSection.querySelector('.destination-header h3');
                let destination = destinationHeader.textContent.replace(/Destination \d+ - /, '').trim();
                
                let hotel = 'Selected Hotel';
                let route = null;
                
                const allListItems = optionContent.querySelectorAll('li');
                allListItems.forEach(item => {
                    const text = item.textContent.trim();
                    
                    if (text.startsWith('Property:')) {
                        hotel = text.split('Property:')[1].trim();
                    }
                    
                    if (text.startsWith('Route:')) {
                        route = text.split('Route:')[1].split('(')[0].trim();
                    }
                });
                
                if (route) {
                    destination = route;
                }
                
                console.log('Found trip details:', {
                    destinationHeader: destinationHeader?.textContent,
                    destination,
                    hotel,
                    route,
                    optionType,
                    allListItems: Array.from(allListItems).map(li => li.textContent)
                });

                const tripMonth = document.querySelector('#travelMonths')?.value;
                const tripLength = document.querySelector('#tripLength')?.value;
                
                console.log('Extracted trip details:', {
                    destination,
                    hotel,
                    tripMonth,
                    tripLength,
                    optionType
                });

                const tripSummary = document.querySelector('.selected-trip-summary');
                if (tripSummary) {
                    // Determine if luxury based on the selected option type, not from the header text
                    const isLuxury = optionType === 'luxury';
                    console.log('MindTrip Section - isLuxury:', isLuxury, 'optionType:', optionType);
                    
                    tripSummary.innerHTML = `
                        <div class="card">
                            <div class="card-header">
                                <h3>Build your Itinerary with MindTrip.ai</h3>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mindtrip-guide p-3">
                                            <h5 class="text-primary mb-3"><i class="fas fa-suitcase"></i> Selected Option</h5>
                                            <div class="selected-details">
                                                <div class="step mb-3">
                                                    <div class="step-content w-100">
                                                        <strong>${isLuxury ? 'Luxury' : 'Economy'} Experience</strong>
                                                        <div class="mt-3">
                                                            <p class="mb-2"><strong>Route:</strong> ${destination}</p>
                                                            <p class="mb-2"><strong>Hotel:</strong> ${hotel}</p>
                                                            <p class="mb-2"><strong>Travel Month:</strong> ${tripMonth || ''}</p>
                                                            <p class="mb-2"><strong>Duration:</strong> ${tripLength ? `${tripLength} days` : ''}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mindtrip-guide p-3">
                                            <h5 class="text-primary mb-3"><i class="fas fa-info-circle"></i> Quick Guide</h5>
                                            <div class="steps-container">
                                                <div class="step mb-3">
                                                    <div class="step-number">1</div>
                                                    <div class="step-content">
                                                        <strong>Click the blue button below</strong>
                                                        <small class="d-block text-muted">This will open MindTrip.ai in a new tab</small>
                                                    </div>
                                                </div>
                                                <div class="step mb-3">
                                                    <div class="step-number">2</div>
                                                    <div class="step-content">
                                                        <strong>Paste into MindTrip Chat</strong>
                                                        <small class="d-block text-muted">Your trip prompt will be added to your clipboard</small>
                                                    </div>
                                                </div>
                                                <div class="step">
                                                    <div class="step-number">3</div>
                                                    <div class="step-content">
                                                        <strong>Start Planning!</strong>
                                                        <small class="d-block text-muted">MindTrip will help build your full itinerary</small>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="text-center mt-4">
                                    <button id="mindtrip-btn" class="btn btn-primary btn-lg mindtrip-btn">
                                        <i class="fas fa-plane-departure me-2"></i> Continue Planning on MindTrip.ai
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    const mindTripBtn = document.getElementById('mindtrip-btn');
                    if (mindTripBtn) {
                        mindTripBtn.addEventListener('click', async () => {
                            const prompt = `I'm planning a ${tripLength}-day ${isLuxury ? 'luxury' : 'budget-friendly'} trip to ${destination} in ${tripMonth}, staying at ${hotel}. Please help me create a detailed day-by-day itinerary that includes:

1. Activities and attractions that match the ${isLuxury ? 'luxury' : 'budget-conscious'} nature of my trip
2. Restaurant recommendations for each day
3. Transportation suggestions
4. Any specific tips for my hotel area
5. Estimated timing for each activity

Please organize this by day (Day 1, Day 2, etc) and consider the local weather and best times for each activity.`;
                            
                            try {
                                await navigator.clipboard.writeText(prompt);
                                
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
                                
                                setTimeout(() => {
                                    notification.remove();
                                    window.open('https://mindtrip.ai/chat', '_blank');
                                }, 3000);
                                
                            } catch (error) {
                                console.error('Error handling MindTrip integration:', error);
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
                
                tripSummary?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });
        
        // Fix for destination toggles
        this.attachToggleListeners();
    },

    processSectionContent(destination, sectionNumber) {
        const economyExperienceRegex = /OPTION A - ECONOMY EXPERIENCE([\s\S]*?)(?=OPTION B - LUXURY EXPERIENCE|$)/;
        const luxuryExperienceRegex = /OPTION B - LUXURY EXPERIENCE([\s\S]*)/;
        
        const economyMatch = destination.match(economyExperienceRegex);
        const luxuryMatch = destination.match(luxuryExperienceRegex);
        
        let economyContent = null;
        let luxuryContent = null;
        
        if (economyMatch && economyMatch[1]) {
            economyContent = this.parseExperienceSection(economyMatch[1].trim(), 'economy');
        }
        
        if (luxuryMatch && luxuryMatch[1]) {
            luxuryContent = this.parseExperienceSection(luxuryMatch[1].trim(), 'luxury');
        }
        
        return {
            economyContent,
            luxuryContent
        };
    },
    
    parseExperienceSection(sectionText, type) {
        // Parse all the details from the text
        const result = {
            type: type
        };
        
        // Extract flight details
        const routeMatch = sectionText.match(/Route:([^\n]+)/);
        if (routeMatch) result.route = routeMatch[1].trim();
        
        const airlineMatch = sectionText.match(/Airline:([^\n]+)/);
        if (airlineMatch) result.airline = airlineMatch[1].trim();
        
        // Extract flight points program - look in the Flight Details section
        const flightSectionMatch = sectionText.match(/Flight Details[\s\S]*?Points Program:([^\n]+)/);
        if (flightSectionMatch) result.points_program = flightSectionMatch[1].trim();
        
        const pointsUsedMatch = sectionText.match(/Points Used:([^\n]+)/);
        if (pointsUsedMatch) result.points_used = pointsUsedMatch[1].trim();
        
        const fareClassMatch = sectionText.match(/Fare Class:([^\n]+)/);
        if (fareClassMatch) result.fare_class = fareClassMatch[1].trim();
        
        // Extract hotel details
        const propertyMatch = sectionText.match(/Property:([^\n]+)/);
        if (propertyMatch) result.property = propertyMatch[1].trim();
        
        // Find the hotel points program by looking for Points Program after Hotel Option
        const hotelSectionMatch = sectionText.match(/Hotel Option[\s\S]*?Points Program:([^\n]+)/);
        if (hotelSectionMatch) result.hotel_points_program = hotelSectionMatch[1].trim();
        
        const totalPointsNeededMatch = sectionText.match(/Total Points Needed:([^\n]+)/);
        if (totalPointsNeededMatch) result.total_points_needed = totalPointsNeededMatch[1].trim();
        
        const propertyDetailsMatch = sectionText.match(/Property Details:([^\n]+)/);
        if (propertyDetailsMatch) result.property_details = propertyDetailsMatch[1].trim();
        
        // Extract value analysis
        const totalPointsUsedMatch = sectionText.match(/Total Points Used:([^\n]+)/);
        if (totalPointsUsedMatch) result.total_points_used = totalPointsUsedMatch[1].trim();
        
        // Extract points needed for flight - look in Value Analysis section
        const valueAnalysisSection = sectionText.match(/Value Analysis[\s\S]*/);
        if (valueAnalysisSection) {
            const flightPointsMatch = valueAnalysisSection[0].match(/(?:Airline|Flight):([^\n]+)/);
            if (flightPointsMatch) result.airline_points = flightPointsMatch[1].trim();
        }
        
        const hotelPointsMatch = sectionText.match(/Hotel:([^\n]+)/);
        if (hotelPointsMatch) result.hotel_points = hotelPointsMatch[1].trim();
        
        const dollarValueSavedMatch = sectionText.match(/Dollar Value Saved:([^\n]+)/);
        if (dollarValueSavedMatch) result.dollar_value_saved = dollarValueSavedMatch[1].trim();
        
        return result;
    },

    attachToggleListeners() {
        // Fix for destination toggles
        document.querySelectorAll('.destination-header').forEach(header => {
            // Remove any existing listeners to prevent duplicates
            const newHeader = header.cloneNode(true);
            if (header.parentNode) {
                header.parentNode.replaceChild(newHeader, header);
            }
            
            // Add the event listener with correct context
            newHeader.addEventListener('click', function(event) {
                // Prevent default and stop propagation
                event.preventDefault();
                event.stopPropagation();
                
                console.log('Destination header clicked directly');
                
                // Toggle active class
                this.classList.toggle('active');
                
                // Find and toggle the content
                const content = this.nextElementSibling;
                if (content && content.classList.contains('destination-content')) {
                    // Force toggle the show class
                    if (content.classList.contains('show')) {
                        content.classList.remove('show');
                        content.style.display = 'none';
                    } else {
                        content.classList.add('show');
                        content.style.display = 'block';
                    }
                    console.log('Content visibility toggled:', content.classList.contains('show'));
                } else {
                    console.warn('Could not find destination content element');
                }
                
                // Toggle the rotation of the arrow
                const toggleIcon = this.querySelector('.toggle-icon');
                if (toggleIcon) {
                    toggleIcon.style.transform = this.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                    console.log('Arrow rotation updated:', toggleIcon.style.transform);
                }
            });
        });
        
        console.log('Toggle listeners attached to', document.querySelectorAll('.destination-header').length, 'destination headers');
    },
    
    toggleDestination(event) {
        // This method is now only used as a fallback
        // The inline function in attachToggleListeners is the primary handler
        const header = event.currentTarget || this;
        header.classList.toggle('active');
        const content = header.nextElementSibling;
        if (content) {
            content.classList.toggle('show');
        }
        
        // Toggle the rotation of the arrow
        const toggleIcon = header.querySelector('.toggle-icon');
        if (toggleIcon) {
            toggleIcon.style.transform = header.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
        }
    },

    formatRecommendations(recommendations) {
        if (!recommendations) return '';
        
        // Skip the "Requirements Match" section completely
        let lines = recommendations.split('<br>');
        let formattedContent = '';
        let skipSection = false;
        let inSection = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Skip the "Requirements Match" section and its content
            if (line.includes('Requirements Match:')) {
                skipSection = true;
                continue;
            }
            
            // When we reach a new section, stop skipping
            if (skipSection && (line.includes('Seasonal Analysis:') || 
                               line.includes('Weather Conditions:') || 
                               line.includes('Local Highlights:') || 
                               line.includes('Points Optimization:') ||
                               line.includes('Award Availability:') ||
                               line.includes('Value Opportunities:'))) {
                skipSection = false;
            }
            
            // If we're in skip mode, continue to next line
            if (skipSection) continue;
            
            // Remove the section numbers (e.g., "2. Seasonal Analysis:", "3. Points Optimization:")
            const cleanedLine = line.replace(/^\d+\.\s+/, '');
            
            if (cleanedLine.endsWith(':')) {
                if (cleanedLine === 'Seasonal Analysis:' || cleanedLine === 'Points Optimization:') {
                    // Skip these section headers completely
                    continue;
                }
                formattedContent += `<h5 class="recommendation-category">${cleanedLine}</h5>`;
                inSection = true;
            } else if (cleanedLine.startsWith('- ') || cleanedLine.startsWith('• ') || cleanedLine.startsWith('✓ ')) {
                formattedContent += `<div class="recommendation-item">${cleanedLine.substring(2)}</div>`;
            } else if (cleanedLine && inSection) {
                // Add all non-header content as recommendation items with bullets
                formattedContent += `<div class="recommendation-item">${cleanedLine}</div>`;
            } else if (cleanedLine) {
                // For content not under a section header, don't add bullets
                formattedContent += `<div>${cleanedLine}</div>`;
            }
        }
        
        return formattedContent;
    },

    formatOptionSection(section) {
        if (!section) return '';
        
        // Get section type (Economy or Luxury) - moved up for use in data-option-type
        const isLuxury = section.fare_class && (
            section.fare_class.includes('Business') || 
            section.fare_class.includes('First') || 
            section.fare_class.includes('Premium')
        );

        let html = `
            <div class="option-section">
                <div class="selected-label">Selected</div>
                <div class="option-content">
        `;
        
        // Flight Details
        html += `<div class="detail-section">`;
        html += `<h3 class="section-title">Flight Details</h3>`;
        html += `<ul>`;
        
        if (section.route) {
            html += `<li><b>Route:</b> ${section.route}</li>`;
        }
        
        if (section.airline) {
            html += `<li><b>Airline:</b> ${section.airline}</li>`;
        }
        
        if (section.points_program) {
            html += `<li><b>Points Program:</b> ${section.points_program}</li>`;
        }
        
        if (section.points_used) {
            html += `<li><b>Points Used:</b> ${section.points_used}</li>`;
        }
        
        if (section.fare_class) {
            html += `<li><b>Fare Class:</b> ${section.fare_class}</li>`;
        }
        
        html += `</ul>`;
        html += `</div>`;
        
        // Hotel Option
        html += `<div class="detail-section">`;
        html += `<h3 class="section-title">Hotel Option</h3>`;
        html += `<ul>`;
        
        if (section.property) {
            html += `<li><b>Property:</b> ${section.property}</li>`;
        }
        
        if (section.hotel_points_program) {
            html += `<li><b>Points Program:</b> ${section.hotel_points_program}</li>`;
        }
        
        if (section.total_points_needed) {
            html += `<li><b>Total Points Needed:</b> ${section.total_points_needed}</li>`;
        }
        
        if (section.property_details) {
            html += `<li><b>Property Details:</b> ${section.property_details}</li>`;
        }
        
        html += `</ul>`;
        html += `</div>`;
        
        // Value Analysis
        html += `<div class="detail-section">`;
        html += `<h3 class="section-title">Value Analysis</h3>`;
        html += `<ul>`;
        
        if (section.total_points_used) {
            html += `<li><b>Total Points Used:</b> ${section.total_points_used}</li>`;
        }
        
        if (section.airline_points) {
            html += `<li><b>Flight:</b> ${section.airline_points}</li>`;
        }
        
        if (section.hotel_points) {
            html += `<li><b>Hotel:</b> ${section.hotel_points}</li>`;
        }
        
        if (section.dollar_value_saved) {
            html += `<li><b>Dollar Value Saved:</b> ${section.dollar_value_saved}</li>`;
        }
        
        html += `</ul>`;
        html += `</div>`;
        
        // Continue Planning button
        html += `<div class="text-center">
            <button class="continue-planning-btn select-trip-option" data-option-type="${isLuxury ? 'luxury' : 'economy'}"><i class="fas fa-plane"></i> Continue Planning</button>
        </div>`;
        
        html += `</div></div>`;
        
        return html;
    },

    handleOptionSelection(button) {
        const optionType = button.dataset.optionType;
        console.log(`Selected ${optionType} option`);
        
        // Remove selection from all options
        document.querySelectorAll('.option-section').forEach(section => {
            section.classList.remove('selected');
        });
        
        // Add selection to parent option section
        const optionSection = button.closest('.option-section');
        if (optionSection) {
            optionSection.classList.add('selected');
        }
        
        // Store selected option type for MindTrip
        window.selectedOption = optionType;
        
        // Call any additional functionality needed when an option is selected
        const tripSummary = document.getElementById('tripSummarySection');
        tripSummary?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    formatExperience(text) {
        if (!text) return '';
        
        const sentences = text.split(/(?<=[.!?])\s+/);
        
        return sentences.map(sentence => {
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

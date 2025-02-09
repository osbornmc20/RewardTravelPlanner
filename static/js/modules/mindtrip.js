document.addEventListener('DOMContentLoaded', function() {
    const mindtripBanner = document.getElementById('mindtrip-integration');
    if (!mindtripBanner) return;

    function updateMindTripState(show) {
        const defaultState = mindtripBanner.querySelector('.default-state');
        const selectedState = mindtripBanner.querySelector('.selected-trip-summary');
        
        if (defaultState) defaultState.style.display = show ? 'none' : 'block';
        if (selectedState) selectedState.style.display = show ? 'block' : 'none';
        
        mindtripBanner.classList.toggle('active', show);
        const mindtripBtn = document.getElementById('mindtrip-btn');
        if (mindtripBtn) mindtripBtn.disabled = !show;
    }

    // Reset selection when new results are loaded
    document.addEventListener('tripResultsLoaded', function() {
        // Clear any existing selections
        document.querySelectorAll('.option-content').forEach(content => {
            content.classList.remove('selected');
        });
        
        updateMindTripState(false);
        
        // Reset trip summary
        const tripSummary = mindtripBanner.querySelector('.trip-summary');
        if (tripSummary) tripSummary.innerHTML = '<p class="mb-0">Loading...</p>';
    });

    // Handle trip option selection
    document.addEventListener('click', function(e) {
        const button = e.target.closest('.select-trip-option');
        if (!button) return;

        const optionType = button.dataset.optionType;
        const optionContent = button.closest('.option-content');
        if (!optionContent) return;
        
        // Remove selection from other options
        document.querySelectorAll('.option-content').forEach(content => {
            content.classList.remove('selected');
        });
        
        // Add selection to clicked option
        optionContent.classList.add('selected');
        
        // Show selected state
        updateMindTripState(true);
        
        // Get trip details from the selected option
        const routeElement = optionContent.querySelector('.detail-box:first-of-type li strong');
        
        let destination = 'Selected Destination';
        let hotel = 'Selected Hotel';
        
        // Extract destination
        if (routeElement && routeElement.textContent === 'Route:') {
            destination = routeElement.parentElement.textContent.split('Route:')[1].trim();
        }
        
        // Extract hotel
        const propertyElements = Array.from(optionContent.querySelectorAll('.detail-box li strong'));
        const propertyElement2 = propertyElements.find(el => el.textContent === 'Property:');
        if (propertyElement2) {
            hotel = propertyElement2.parentElement.textContent.split('Property:')[1].trim();
        }

        // Get trip month and length
        const tripMonth = document.querySelector('#travelMonths')?.value;
        const tripLength = document.querySelector('#tripLength')?.value;

        // Use the full travel date range
        let formattedMonth = tripMonth || '';
        
        const tripDetails = {
            type: optionType,
            destination: destination,
            hotel: hotel,
            month: formattedMonth,
            duration: tripLength ? `${tripLength} days` : ''
        };
        
        // Update trip summary
        const tripSummary = mindtripBanner.querySelector('.trip-summary');
        if (tripSummary) {
            tripSummary.innerHTML = `
                <div class="mb-2">
                    <span class="badge ${tripDetails.type === 'luxury' ? 'bg-warning text-dark' : 'bg-info'} mb-2">
                        ${tripDetails.type === 'luxury' ? 'Luxury' : 'Economy'} Experience
                    </span>
                </div>
                <div class="text-start">
                    <p class="mb-2"><strong>Route:</strong> ${tripDetails.destination}</p>
                    <p class="mb-2"><strong>Hotel:</strong> ${tripDetails.hotel}</p>
                    <p class="mb-2"><strong>Travel Month:</strong> ${tripDetails.month}</p>
                    <p class="mb-0"><strong>Duration:</strong> ${tripDetails.duration}</p>
                </div>
            `;
        }
        
        // Enable and update the MindTrip button
        const mindtripBtn = document.getElementById('mindtrip-btn');
        mindtripBtn.disabled = false;
        
        // Scroll to the MindTrip banner
        mindtripBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // Handle MindTrip button click
    const mindTripBtn = document.getElementById('mindtrip-btn');
    if (mindTripBtn) {
        mindTripBtn.addEventListener('click', async () => {
            const selectedOption = document.querySelector('.option-content.selected');
            if (!selectedOption) {
                console.log('No option selected');
                return;
            }

            // Get the trip type from the selected option button
            const optionType = selectedOption.querySelector('.select-trip-option').dataset.optionType;
            const tripSummary = document.querySelector('.trip-summary').innerHTML;
            
            // Parse destination and hotel from trip summary
            const lines = tripSummary.split('<br>');
            const destination = lines[1].split('<strong>Route:</strong>')[1].trim();
            const hotel = lines[2].split('<strong>Hotel:</strong>')[1].trim();
            const tripMonth = lines[3].split('<strong>Travel Month:</strong>')[1].trim();
            const tripLength = lines[4].split('<strong>Duration:</strong>')[1].trim().split(' ')[0];

            // Extract destination city (remove 'LAX to ' if present)
            const destinationCity = destination.split(' to ')[1] || destination;

            // Create the prompt
            const prompt = `${tripLength}-day ${optionType === 'luxury' ? 'luxury' : 'budget-friendly'} trip to ${destinationCity}, ${tripMonth}. Staying at ${hotel}.

Please create a day-by-day itinerary with:
1. Must-see attractions and hidden gems
2. ${optionType === 'luxury' ? 'Upscale' : 'Value-conscious'} restaurant recommendations
3. Transportation tips and best times to visit
4. Special events in ${tripMonth}
5. Local experiences

Consider:
- Hotel location for planning
- Mix of scheduled/free time
- ${optionType === 'luxury' ? 'Premium experiences' : 'Good value activities'}
- Weather and crowds

For each day include:
- Morning activities
- Afternoon plans
- Evening activities
- Dining suggestions`;

            try {
                // Copy to clipboard
                await navigator.clipboard.writeText(prompt);
                
                // Create and show success notification
                const notification = document.createElement('div');
                notification.className = 'alert alert-success position-fixed';
                notification.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    padding: 15px 25px;
                    border-radius: 8px;
                    background-color: rgba(40, 167, 69, 0.95);
                    color: white;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-weight: 500;
                    backdrop-filter: blur(8px);
                    max-width: 400px;
                    width: 90%;
                    transition: all 0.3s ease;
                `;
                notification.innerHTML = `
                    <i class="fas fa-check-circle" style="font-size: 1.4em;"></i>
                    <div>
                        <div class="mb-1">Trip details copied to clipboard!</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">Opening MindTrip in 3 seconds...</div>
                    </div>
                `;
                document.body.appendChild(notification);

                // Wait 3 seconds then open MindTrip
                setTimeout(() => {
                    notification.remove();
                    window.open('https://mindtrip.ai/chat/', '_blank');
                }, 3000);
            } catch (error) {
                console.error('Error:', error);
                // Show error notification
                const errorNotification = document.createElement('div');
                errorNotification.className = 'alert alert-danger position-fixed';
                errorNotification.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    padding: 15px 25px;
                    border-radius: 5px;
                    background-color: #dc3545;
                    color: white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 500;
                `;
                errorNotification.innerHTML = `
                    <i class="fas fa-exclamation-circle" style="font-size: 1.2em;"></i>
                    Unable to copy automatically. Please copy the details manually in MindTrip.
                `;
                document.body.appendChild(errorNotification);
                
                // Open MindTrip after a short delay even if copy fails
                setTimeout(() => {
                    errorNotification.remove();
                    window.open('https://mindtrip.ai/chat/', '_blank');
                }, 3000);
            }
        });
    }
});        });
    }
}

// Copy to clipboard and show notification
async function copyToClipboardAndNotify(text) {
    try {
        // Copy to clipboard
        await navigator.clipboard.writeText(text);
        
        // Create and show success notification
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
            Trip details copied to clipboard! Opening MindTrip in 3 seconds...
        `;
        document.body.appendChild(notification);

        // Wait 3 seconds then open MindTrip
        setTimeout(() => {
            notification.remove();
            window.open('https://mindtrip.ai/chat/', '_blank');
        }, 3000);
    } catch (error) {
        console.error('Error:', error);
        // Show error notification
        const errorNotification = document.createElement('div');
        errorNotification.className = 'alert alert-danger position-fixed';
        errorNotification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            padding: 15px 25px;
            border-radius: 5px;
            background-color: #dc3545;
            color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
        `;
        errorNotification.innerHTML = `
            <i class="fas fa-exclamation-circle" style="font-size: 1.2em;"></i>
            Unable to copy automatically. Please copy the details manually in MindTrip.
        `;
        document.body.appendChild(errorNotification);
        
        // Open MindTrip after a short delay even if copy fails
        setTimeout(() => {
            errorNotification.remove();
            window.open('https://mindtrip.ai/chat/', '_blank');
        }, 3000);
    }
}

// Initialize MindTrip functionality
document.addEventListener('DOMContentLoaded', function() {
    const mindTripBtn = document.getElementById('mindtrip-btn');
    if (mindTripBtn) {
        mindTripBtn.addEventListener('click', async () => {
            const selectedOption = document.querySelector('.option-content.selected');
            await handleMindTripClick(selectedOption);
        });
    }
});

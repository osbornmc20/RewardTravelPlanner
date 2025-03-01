/**
 * Destination Toggle Script
 * Handles toggling destination sections open and closed
 * 
 * NOTE: This script is now DISABLED to avoid conflicts with trip_generator.js
 * The toggle functionality is now handled directly in trip_generator.js
 */

// This script is disabled to avoid conflicts with trip_generator.js
console.log('Destination toggle script loaded but disabled to avoid conflicts');

// For reference only - the functionality has been moved to trip_generator.js
function disabledCode() {
    // This code is kept for reference but is not executed
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Destination toggle script loaded');
        
        // Add direct document click handler for destination headers
        document.addEventListener('click', function(e) {
            // Check if the click was on a header or its child elements
            const header = e.target.closest('.destination-header');
            if (header) {
                e.preventDefault();
                e.stopPropagation();
                
                // Toggle active class on header
                header.classList.toggle('active');
                
                // Find the content element (next sibling)
                const content = header.nextElementSibling;
                if (content && content.classList.contains('destination-content')) {
                    // Toggle visibility
                    content.classList.toggle('show');
                    console.log('Toggled content visibility:', content, content.classList.contains('show'));
                }
                
                // Rotate the toggle icon
                const toggleIcon = header.querySelector('.toggle-icon');
                if (toggleIcon) {
                    toggleIcon.style.transform = header.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            }
        });
    });
}

// These functions are disabled and kept for reference only

// Function to add listeners - DISABLED
function addDestinationToggleListeners_disabled() {
    // Remove existing listeners first to prevent duplicates
    document.querySelectorAll('.destination-header').forEach(header => {
        // Use cloning technique to remove any existing events
        const newHeader = header.cloneNode(true);
        if (header.parentNode) {
            header.parentNode.replaceChild(newHeader, header);
        }
    });
    
    // Now add fresh click handlers to all destination headers
    document.querySelectorAll('.destination-header').forEach(header => {
        header.addEventListener('click', handleDestinationToggle_disabled);
        console.log('Added toggle listener to:', header);
    });
    
    console.log('Total destination headers with listeners:', document.querySelectorAll('.destination-header').length);
}

// Handler function for toggling - DISABLED
function handleDestinationToggle_disabled(event) {
    console.log('Destination toggle clicked', this);
    
    // Toggle active class on header
    this.classList.toggle('active');
    
    // Toggle show class on content
    const content = this.nextElementSibling;
    if (content && content.classList.contains('destination-content')) {
        content.classList.toggle('show');
        console.log('Toggled content visibility:', content.classList.contains('show'));
    } else {
        console.warn('Could not find destination content element');
    }
    
    // Rotate toggle icon
    const toggleIcon = this.querySelector('.toggle-icon');
    if (toggleIcon) {
        toggleIcon.style.transform = this.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
        console.log('Rotated toggle icon:', toggleIcon.style.transform);
    }
    
    // Prevent event from bubbling
    event.stopPropagation();
    
    // Also prevent the default action if this was triggered by a click
    if (event) {
        event.preventDefault();
    }
}

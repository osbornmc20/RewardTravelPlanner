/**
 * Enhanced Google Analytics 4 event tracking
 * This file contains custom event tracking for the Travel Rewards App
 */

(function() {
    // Check if gtag is available
    function isGtagAvailable() {
        return typeof gtag === 'function';
    }

    // Track page views with enhanced parameters
    function trackPageView() {
        if (!isGtagAvailable()) return;
        
        // Get page metadata
        const pageTitle = document.title;
        const pageUrl = window.location.href;
        const pagePath = window.location.pathname;
        
        // Send pageview with additional parameters
        gtag('event', 'page_view', {
            page_title: pageTitle,
            page_location: pageUrl,
            page_path: pagePath
        });
    }

    // Track outbound links
    function trackOutboundLinks() {
        if (!isGtagAvailable()) return;
        
        document.addEventListener('click', function(e) {
            // Find closest anchor tag
            let target = e.target;
            while (target && target.tagName !== 'A') {
                target = target.parentNode;
                if (!target) return;
            }
            
            // Check if it's an external link
            if (target.hostname !== window.location.hostname) {
                gtag('event', 'outbound_link', {
                    link_url: target.href,
                    link_domain: target.hostname,
                    link_text: target.innerText || 'Unknown'
                });
            }
        });
    }

    // Track form submissions
    function trackFormSubmissions() {
        if (!isGtagAvailable()) return;
        
        document.addEventListener('submit', function(e) {
            const form = e.target;
            const formId = form.id || 'unknown_form';
            const formAction = form.action || 'unknown_action';
            
            gtag('event', 'form_submit', {
                form_id: formId,
                form_action: formAction,
                form_name: form.getAttribute('name') || 'unnamed'
            });
        });
    }

    // Track search queries
    function trackSearchQueries() {
        if (!isGtagAvailable()) return;
        
        // Find search forms
        const searchForms = document.querySelectorAll('form[role="search"], form.search-form');
        
        searchForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Find search input
                const searchInput = form.querySelector('input[type="search"], input[name="q"], input[name="query"], input[name="s"]');
                if (searchInput && searchInput.value) {
                    gtag('event', 'search', {
                        search_term: searchInput.value
                    });
                }
            });
        });
    }

    // Initialize all tracking
    function initTracking() {
        trackPageView();
        trackOutboundLinks();
        trackFormSubmissions();
        trackSearchQueries();
        
        // Track custom events for travel app
        trackTravelAppEvents();
    }

    // Custom events specific to the travel app
    function trackTravelAppEvents() {
        if (!isGtagAvailable()) return;
        
        // Track trip planner interactions
        const tripForm = document.querySelector('#trip-form');
        if (tripForm) {
            tripForm.addEventListener('submit', function() {
                gtag('event', 'trip_search', {
                    event_category: 'engagement',
                    event_label: 'Trip Search'
                });
            });
        }
        
        // Track review clicks
        document.addEventListener('click', function(e) {
            let target = e.target;
            while (target && !target.classList.contains('review-card')) {
                target = target.parentNode;
                if (!target) return;
            }
            
            if (target.classList.contains('review-card')) {
                const reviewTitle = target.querySelector('.card-title')?.innerText || 'Unknown Review';
                gtag('event', 'review_click', {
                    event_category: 'engagement',
                    event_label: reviewTitle
                });
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTracking);
    } else {
        initTracking();
    }
})();

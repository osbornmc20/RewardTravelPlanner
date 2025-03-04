/**
 * Simple error tracking for the Travel Rewards App
 * Logs client-side errors to the console and sends them to the server
 */

(function() {
    // Initialize error tracking
    function initErrorTracking() {
        // Listen for unhandled errors
        window.addEventListener('error', function(event) {
            logError({
                type: 'uncaught_error',
                message: event.message,
                source: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error ? event.error.stack : null,
                url: window.location.href
            });
        });

        // Listen for unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            logError({
                type: 'unhandled_promise_rejection',
                message: event.reason ? (event.reason.message || String(event.reason)) : 'Unknown promise rejection',
                stack: event.reason && event.reason.stack ? event.reason.stack : null,
                url: window.location.href
            });
        });
    }

    // Log error to console and send to server
    function logError(errorData) {
        // Log to console
        console.error('Error tracked:', errorData);

        // Send to server
        fetch('/api/log-error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(errorData)
        }).catch(function(err) {
            // Don't try to report errors in the error reporter
            console.error('Failed to send error report:', err);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initErrorTracking);
    } else {
        initErrorTracking();
    }
})();

class RecommendationsModule {
    constructor() {
        this.container = document.querySelector('.recommendations-grid');
        this.recommendations = [];
        this.init();
    }

    init() {
        this.loadRecommendations();
    }

    loadRecommendations() {
        // This will be replaced with actual data from the backend
        fetch('/api/recommendations')
            .then(response => response.json())
            .then(data => {
                this.recommendations = data;
                this.renderRecommendations();
            })
            .catch(error => console.error('Error loading recommendations:', error));
    }

    renderRecommendations() {
        this.container.innerHTML = this.recommendations.map(rec => this.createRecommendationCard(rec)).join('');
    }

    createRecommendationCard(recommendation) {
        return `
            <a href="${recommendation.url}" target="_blank" class="recommendation-card">
                <img src="${recommendation.image}" alt="${recommendation.title}" class="recommendation-image">
                <div class="recommendation-content">
                    <h3 class="recommendation-title">${recommendation.title}</h3>
                    <div class="recommendation-location">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${recommendation.location}</span>
                    </div>
                </div>
            </a>
        `;
    }
}

// Initialize the module
document.addEventListener('DOMContentLoaded', () => {
    new RecommendationsModule();
});

class TravelGuidesModule {
    constructor() {
        this.container = document.querySelector('.travel-guides-grid');
        this.recommendations = [];
        this.init();
    }

    init() {
        this.loadRecommendations();
    }

    loadRecommendations() {
        // This will be replaced with actual data from the backend
        fetch('/api/travel-guides')
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
        const imagePath = recommendation.image;
        const thumbnailPath = imagePath.replace('.jpg', '-thumb.jpg');
        const datePublished = new Date().toISOString().split('T')[0];
        
        // Create structured data for this guide
        const structuredData = {
            '@context': 'https://schema.org',
            '@type': 'TravelGuide',
            'name': recommendation.title,
            'description': `Travel guide for ${recommendation.location}`,
            'publisher': {
                '@type': 'Organization',
                'name': 'Go Ask Marshall',
                'url': 'https://goaskmarshall.com'
            },
            'datePublished': datePublished,
            'dateModified': datePublished,
            'image': imagePath,
            'about': {
                '@type': 'Place',
                'name': recommendation.location
            }
        };
        
        return `
            <article class="travel-guide-card" itemscope itemtype="https://schema.org/TravelGuide">
                <script type="application/ld+json">
                    ${JSON.stringify(structuredData)}
                </script>
                <a href="${recommendation.url}" 
                   target="_blank" 
                   class="travel-guide-link"
                   aria-label="Read more about ${recommendation.title}"
                   itemprop="url">
                    <img src="${thumbnailPath}" 
                         alt="Travel guide for ${recommendation.location}" 
                         class="travel-guide-image"
                         loading="lazy"
                         onload="this.classList.add('loaded')"
                         srcset="${thumbnailPath} 300w,
                                 ${imagePath} 600w"
                         sizes="(max-width: 768px) 100vw,
                                (max-width: 1200px) 50vw,
                                33vw"
                         itemprop="image">
                    <div class="travel-guide-content">
                        <h2 class="travel-guide-title" itemprop="name">${recommendation.title}</h2>
                        <div class="travel-guide-location" aria-label="Location">
                            <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                            <span itemprop="about" itemscope itemtype="https://schema.org/Place">
                                <span itemprop="name">${recommendation.location}</span>
                            </span>
                        </div>
                    </div>
                </a>
            </article>
        `;
    }
}

// Initialize the module
document.addEventListener('DOMContentLoaded', () => {
    new TravelGuidesModule();
});

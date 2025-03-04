class TravelGuidesModule {
    constructor() {
        this.guidesContainer = document.querySelector('.travel-guides-grid');
        this.reviewsContainer = document.querySelector('.reviews-grid');
        this.guides = [];
        this.reviews = [];
        this.init();
    }

    init() {
        this.loadGuides();
        this.loadReviews();
    }

    loadGuides() {
        // Load travel guides from the backend
        fetch('/api/travel-guides')
            .then(response => response.json())
            .then(data => {
                this.guides = data;
                this.renderGuides();
            })
            .catch(error => console.error('Error loading guides:', error));
    }
    
    loadReviews() {
        // Load reviews from the backend
        fetch('/api/reviews')
            .then(response => response.json())
            .then(data => {
                this.reviews = data.reviews || [];
                
                // Add URL property to each review for linking to the review page
                this.reviews = this.reviews.map(review => ({
                    ...review,
                    url: `/reviews/${review.slug}`
                }));
                
                this.renderReviews();
            })
            .catch(error => console.error('Error loading reviews:', error));
    }

    renderGuides() {
        this.guidesContainer.innerHTML = this.guides.map(guide => this.createGuideCard(guide)).join('');
    }
    
    renderReviews() {
        if (!this.reviewsContainer) return;
        
        if (this.reviews.length === 0) {
            // Hide the reviews section if there are no reviews
            const reviewsSection = this.reviewsContainer.closest('section');
            const reviewsTitle = reviewsSection.previousElementSibling;
            reviewsSection.style.display = 'none';
            reviewsTitle.style.display = 'none';
            return;
        }
        
        // Show the reviews section if there are reviews
        const reviewsSection = this.reviewsContainer.closest('section');
        const reviewsTitle = reviewsSection.previousElementSibling;
        reviewsSection.style.display = 'block';
        reviewsTitle.style.display = 'block';
        
        this.reviewsContainer.innerHTML = this.reviews.map(review => this.createReviewCard(review)).join('');
    }

    createGuideCard(guide) {
        const imagePath = guide.image;
        const thumbnailPath = imagePath.replace('.jpg', '-thumb.jpg');
        const datePublished = new Date().toISOString().split('T')[0];
        
        // Create structured data for this guide
        const structuredData = {
            '@context': 'https://schema.org',
            '@type': 'TravelGuide',
            'name': guide.title,
            'description': `Travel guide for ${guide.location}`,
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
                'name': guide.location
            }
        };
        
        return `
            <article class="travel-guide-card" itemscope itemtype="https://schema.org/TravelGuide">
                <script type="application/ld+json">
                    ${JSON.stringify(structuredData)}
                </script>
                <a href="${guide.url}" 
                   target="_blank" 
                   class="travel-guide-link"
                   aria-label="Read more about ${guide.title}"
                   itemprop="url">
                    <img src="${thumbnailPath}" 
                         alt="Travel guide for ${guide.location}" 
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
                        <h2 class="travel-guide-title" itemprop="name">${guide.title}</h2>
                        <div class="travel-guide-location" aria-label="Location">
                            <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                            <span itemprop="about" itemscope itemtype="https://schema.org/Place">
                                <span itemprop="name">${guide.location}</span>
                            </span>
                        </div>
                    </div>
                </a>
            </article>
        `;
    }
    
    createReviewCard(review) {
        // Create structured data for this review
        const structuredData = {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': review.title,
            'description': review.summary,
            'image': review.image,
            'datePublished': review.created_at,
            'author': {
                '@type': 'Person',
                'name': review.author
            },
            'publisher': {
                '@type': 'Organization',
                'name': 'Go Ask Marshall',
                'url': 'https://goaskmarshall.com'
            }
        };
        
        return `
            <article class="travel-guide-card" itemscope itemtype="https://schema.org/Article">
                <script type="application/ld+json">
                    ${JSON.stringify(structuredData)}
                </script>
                <a href="${review.url}" 
                   class="travel-guide-link"
                   aria-label="Read more about ${review.title}"
                   itemprop="url">
                    <img src="${review.image}" 
                         alt="${review.title}" 
                         class="travel-guide-image"
                         loading="lazy"
                         onload="this.classList.add('loaded')"
                         itemprop="image">
                    <div class="travel-guide-content">
                        <h2 class="travel-guide-title" itemprop="headline">${review.title}</h2>
                        <div class="travel-guide-location" aria-label="Location">
                            <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
                            <span>${review.location}</span>
                        </div>
                        <p class="review-summary" itemprop="description">${review.summary}</p>
                        <div class="review-meta">
                            <span class="review-date">
                                <i class="far fa-calendar-alt" aria-hidden="true"></i> ${review.created_at}
                            </span>
                            <span class="review-author" itemprop="author" itemscope itemtype="https://schema.org/Person">
                                <i class="far fa-user" aria-hidden="true"></i> 
                                <span itemprop="name">${review.author}</span>
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

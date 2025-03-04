#!/bin/bash
# Deploy script for Render deployment
# This script should be run on the Render server during deployment

echo "Starting deployment process..."

# Create all tables if they don't exist
echo "Creating database tables..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Check if the reviews table exists and has content
echo "Checking for existing reviews..."
REVIEW_COUNT=$(python -c "from app import app, db; from models.review import Review; app.app_context().push(); print(Review.query.count())")

if [ "$REVIEW_COUNT" -eq "0" ]; then
    echo "No reviews found in the database. Importing sample reviews..."
    
    # Import reviews from the SQL file if it exists
    if [ -f "reviews_for_production.sql" ]; then
        echo "Found reviews_for_production.sql, importing..."
        
        # Run SQL script
        python -c "
import sqlite3
from app import app, db
from models.review import Review
import json
import os
from datetime import datetime

# Sample reviews data - edit this to match your reviews
sample_reviews = [
    {
        'title': 'Hidden Gem Hotels in Mexico',
        'slug': 'hidden-gem-hotels-in-mexico',
        'location': 'Mexico',
        'summary': 'Here are a few lesser-known beach hotels in Mexico worth checking out if you are in need of a place to relax without the crowds.',
        'content': '# Hidden Gem Hotels in Mexico\n\n## Introduction\nMexico is known for its stunning beaches, vibrant culture, and delicious cuisine. For those seeking unique and luxurious accommodations without breaking the bank, boutique hotels are the perfect option. We have tracked down five amazing places to stay that will provide you with an unforgettable experience on your next trip!',
        'image': 'static/images/blog/mexico_hotels/Marea Beachfront Villas.jpg',
        'author': 'Go Ask Marshall',
        'is_published': True
    },
    {
        'title': 'Mexico\'s Secret Beach Destinations: Escape the Crowds',
        'slug': 'mexico-s-secret-beach-destinations-escape-the-crowds',
        'location': 'Mexico',
        'summary': 'Discover the hidden coastal gems of Mexico where you can enjoy pristine beaches away from the tourist crowds. This guide reveals serene and stunning beaches that offer authentic experiences and natural beauty.',
        'content': '# Mexico\'s Secret Beach Destinations: Escape the Crowds\n\n## Introduction\nMexico\'s coastline stretches over 5,800 miles, offering countless beaches beyond the well-known tourist hubs of Cancun and Cabo San Lucas. For travelers seeking tranquility, pristine natural settings, and authentic experiences, these lesser-known beach destinations provide the perfect escape.',
        'image': 'static/images/blog/mexico_beaches/Playa Xpu-Ha.webp',
        'author': 'Go Ask Marshall',
        'is_published': True
    },
    {
        'title': 'Hotel El Ganzo: A Boutique Luxury Experience in San Jose del Cabo',
        'slug': 'hotel-el-ganzo-a-boutique-luxury-experience-in-san-jose-del-cabo',
        'location': 'San Jose del Cabo, Mexico',
        'summary': 'Discover Hotel El Ganzo, a unique boutique hotel in San Jose del Cabo offering oceanfront views, artistic ambiance, and exclusive amenities. Perfect for travelers seeking luxury with character away from crowded tourist spots.',
        'content': '# Hotel El Ganzo: A Boutique Luxury Experience in San Jose del Cabo\n\n## Introduction\nLocated in the peaceful surroundings of San Jose Del Cabo, Hotel El Ganzo offers more than just a common getaway. It provides an escape from the busy and overcrowded resort areas.',
        'image': '/static/images/blog/el_ganzo/El%20Ganzo%20Header%20Image.jpg',
        'author': 'Go Ask Marshall',
        'is_published': True
    }
]

with app.app_context():
    # Add the sample reviews
    for review_data in sample_reviews:
        existing = Review.query.filter_by(slug=review_data['slug']).first()
        if not existing:
            review = Review(
                title=review_data['title'],
                location=review_data['location'],
                summary=review_data['summary'],
                content=review_data['content'],
                image=review_data['image'],
                author=review_data.get('author', 'Go Ask Marshall')
            )
            review.slug = review_data['slug']
            review.is_published = review_data.get('is_published', True)
            db.session.add(review)
    
    db.session.commit()
    print(f'Added {len(sample_reviews)} sample reviews to the database')
        "
    else
        echo "reviews_for_production.sql not found. Skipping review import."
    fi
else
    echo "Found $REVIEW_COUNT reviews in the database. Skipping sample reviews import."
fi

echo "Deployment complete!"

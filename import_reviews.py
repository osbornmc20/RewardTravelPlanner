#!/usr/bin/env python3
"""
Import Reviews Script

This script imports reviews from a JSON file into the database.
It can be run on the production server to import reviews exported from the local database.

Usage:
  python3 import_reviews.py
"""

import json
import os
from app import app, db
from models.review import Review

def import_reviews():
    """Import reviews from a JSON file"""
    
    # Check if the file exists
    if not os.path.exists('reviews_export.json'):
        print("reviews_export.json file not found.")
        return
    
    # Load the reviews data
    with open('reviews_export.json', 'r') as f:
        reviews_data = json.load(f)
    
    if not reviews_data:
        print("No reviews found in the JSON file.")
        return
    
    print(f"Found {len(reviews_data)} reviews to import.")
    
    with app.app_context():
        # Check for existing reviews to avoid duplicates
        existing_slugs = [r.slug for r in Review.query.all()]
        
        reviews_added = 0
        reviews_updated = 0
        
        # Add each review
        for review_data in reviews_data:
            # Check if the review already exists
            if review_data['slug'] in existing_slugs:
                # Update existing review
                existing = Review.query.filter_by(slug=review_data['slug']).first()
                existing.title = review_data['title']
                existing.location = review_data['location']
                existing.summary = review_data['summary']
                existing.content = review_data['content']
                existing.image = review_data['image']
                existing.author = review_data.get('author', 'Go Ask Marshall')
                existing.is_published = review_data.get('is_published', True)
                reviews_updated += 1
                print(f"Updated review: {review_data['title']}")
            else:
                # Create a new review
                review = Review(
                    title=review_data['title'],
                    slug=review_data['slug'],
                    location=review_data['location'],
                    summary=review_data['summary'],
                    content=review_data['content'],
                    image=review_data['image'],
                    author=review_data.get('author', 'Go Ask Marshall'),
                    is_published=review_data.get('is_published', True)
                )
                db.session.add(review)
                reviews_added += 1
                print(f"Added review: {review_data['title']}")
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully imported reviews: {reviews_added} added, {reviews_updated} updated")

if __name__ == "__main__":
    import_reviews()

#!/usr/bin/env python3
"""
Export Reviews Script

This script exports all reviews from the local database to a JSON file that can be
imported on the production server.

Usage:
  python3 export_reviews.py
"""

import json
import os
from app import app, db
from models.review import Review

def export_reviews():
    """Export all reviews to a JSON file"""
    
    with app.app_context():
        # Get all reviews
        reviews = Review.query.all()
        
        if not reviews:
            print("No reviews found in the database.")
            return
        
        # Convert to JSON-serializable format
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                "title": review.title,
                "slug": review.slug,
                "location": review.location,
                "summary": review.summary,
                "content": review.content,
                "image": review.image,
                "author": review.author,
                "is_published": review.is_published
            })
        
        # Write to file
        with open('reviews_export.json', 'w') as f:
            json.dump(reviews_data, f, indent=2)
        
        print(f"Successfully exported {len(reviews)} reviews to reviews_export.json")

if __name__ == "__main__":
    export_reviews()

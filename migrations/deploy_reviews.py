#!/usr/bin/env python3
"""
Deploy Reviews Migration

This script creates a proper database migration that can be run on the production server
to add the sample reviews to the database. It can be included in your deployment process
or run manually on the server.

Usage:
  python migrations/deploy_reviews.py
"""

from flask import Flask
from flask_migrate import Migrate
import os
import sys
import json
from datetime import datetime

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app and database
from app import app, db
from models.review import Review

def deploy_reviews():
    """Deploy reviews to the production database"""
    
    # Get the reviews from the JSON file
    try:
        with open('reviews_for_production.json', 'r') as f:
            reviews_data = json.load(f)
            
        if not reviews_data:
            print("No reviews found in the JSON file.")
            return False
    except FileNotFoundError:
        print("reviews_for_production.json file not found. Run upload_reviews_to_render.py first.")
        return False
    except json.JSONDecodeError:
        print("Error parsing the JSON file. Make sure it's valid JSON.")
        return False
    
    print(f"Found {len(reviews_data)} reviews to deploy.")
    
    # Initialize Flask app context
    with app.app_context():
        # Make sure the reviews table exists
        db.create_all()
        
        # Check for existing reviews to avoid duplicates
        existing_slugs = [r.slug for r in Review.query.all()]
        
        reviews_added = 0
        reviews_skipped = 0
        
        # Add each review
        for review_data in reviews_data:
            # Skip if the review already exists
            if review_data['slug'] in existing_slugs:
                print(f"Review '{review_data['title']}' already exists. Skipping.")
                reviews_skipped += 1
                continue
            
            # Create a new review object
            review = Review(
                title=review_data['title'],
                location=review_data['location'],
                summary=review_data['summary'],
                content=review_data['content'],
                image=review_data['image'],
                author=review_data.get('author', 'Go Ask Marshall')
            )
            
            # Set other attributes
            review.slug = review_data['slug']  # Use the existing slug
            review.is_published = review_data.get('is_published', True)
            
            # Parse dates if they exist
            if 'created_at' in review_data and review_data['created_at']:
                try:
                    review.created_at = datetime.strptime(review_data['created_at'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If date parsing fails, use current time
                    pass
                    
            if 'updated_at' in review_data and review_data['updated_at']:
                try:
                    review.updated_at = datetime.strptime(review_data['updated_at'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If date parsing fails, use current time
                    pass
            
            # Add and commit
            db.session.add(review)
            reviews_added += 1
            
        # Commit all changes at once
        try:
            db.session.commit()
            print(f"Successfully added {reviews_added} reviews to the database.")
            print(f"Skipped {reviews_skipped} reviews that already existed.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error adding reviews to the database: {str(e)}")
            return False

if __name__ == "__main__":
    # Create migrations directory if it doesn't exist
    os.makedirs('migrations', exist_ok=True)
    
    # Deploy reviews
    deploy_reviews()

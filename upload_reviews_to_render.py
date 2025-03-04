#!/usr/bin/env python3
"""
Upload Reviews to Production

This script exports reviews from your local database and provides instructions for importing them
to the production database on Render. It creates a SQL script with INSERT statements that
can be executed on the production database.

Usage:
  python3 upload_reviews_to_render.py
"""

import json
import os
import sqlite3
from datetime import datetime

def export_reviews_to_sql():
    """Export reviews from local database to SQL insert statements"""
    
    # Connect to local database
    local_db_path = os.path.join('instance', 'travel_planner.db')
    if not os.path.exists(local_db_path):
        print(f"Error: Local database not found at {local_db_path}")
        return False
        
    conn = sqlite3.connect(local_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all reviews
    cursor.execute("""
        SELECT id, title, slug, location, summary, content, image, author, 
               created_at, updated_at, is_published
        FROM reviews
    """)
    
    reviews = cursor.fetchall()
    
    if not reviews:
        print("No reviews found in local database.")
        return False
    
    # Create SQL file with insert statements
    with open('reviews_for_production.sql', 'w') as f:
        f.write("-- Reviews exported for production database\n")
        f.write("-- Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        
        # Check if table exists and create it if not
        f.write("""
-- First, check if reviews table exists and create it if not
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(500),
    author VARCHAR(100) DEFAULT 'Go Ask Marshall',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT 1
);

""")
        
        # Add insert statements
        for review in reviews:
            # Format date fields properly
            created_at = review['created_at'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_at = review['updated_at'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Escape single quotes in strings
            title = review['title'].replace("'", "''")
            slug = review['slug'].replace("'", "''")
            location = review['location'].replace("'", "''")
            summary = review['summary'].replace("'", "''") if review['summary'] else ''
            content = review['content'].replace("'", "''") if review['content'] else ''
            image = review['image'].replace("'", "''") if review['image'] else ''
            author = review['author'].replace("'", "''") if review['author'] else 'Go Ask Marshall'
            
            # Write INSERT statement
            f.write(f"""-- Review: {title}
INSERT OR IGNORE INTO reviews (title, slug, location, summary, content, image, author, created_at, updated_at, is_published)
VALUES (
    '{title}',
    '{slug}',
    '{location}',
    '{summary}',
    '{content}',
    '{image}',
    '{author}',
    '{created_at}',
    '{updated_at}',
    {1 if review['is_published'] else 0}
);

""")
    
    # Also export as JSON for reference
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, slug, location, summary, content, image, author, 
               created_at, updated_at, is_published
        FROM reviews
    """)
    
    reviews_json = []
    for row in cursor.fetchall():
        reviews_json.append({
            'title': row['title'],
            'slug': row['slug'],
            'location': row['location'],
            'summary': row['summary'],
            'content': row['content'],
            'image': row['image'],
            'author': row['author'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'is_published': bool(row['is_published'])
        })
    
    with open('reviews_for_production.json', 'w') as f:
        json.dump(reviews_json, f, indent=2)
    
    print("Also exported reviews to reviews_for_production.json for reference")
    
    return True

def print_instructions():
    """Print instructions for uploading to production"""
    print("\n" + "="*80)
    print("INSTRUCTIONS FOR UPLOADING REVIEWS TO PRODUCTION")
    print("="*80)
    print("""
1. This script has generated a SQL file (reviews_for_production.sql) with all the 
   reviews from your local database.

2. To upload these reviews to your Render production database, you have several options:

   Option A: Use the Render Database Shell (easiest method)
   - Log in to your Render dashboard
   - Go to your PostgreSQL database
   - Click "Shell" in the dashboard
   - Copy and paste the contents of reviews_for_production.sql into the shell
   - Run the SQL commands

   Option B: Use a migration script in your app
   - Copy the SQL from reviews_for_production.sql
   - Create a new migration file in your app
   - Deploy your app with the migration

   Option C: Use a database management tool
   - Connect to your Render PostgreSQL database using a tool like DBeaver, pgAdmin, etc.
   - Run the SQL commands from reviews_for_production.sql

3. After uploading, refresh your website and the reviews should appear.

Note: The SQL file is designed to be safe to run multiple times - it uses INSERT OR IGNORE
to prevent duplicate entries.
""")

if __name__ == "__main__":
    if export_reviews_to_sql():
        print(f"Successfully exported reviews to reviews_for_production.sql")
        print_instructions()

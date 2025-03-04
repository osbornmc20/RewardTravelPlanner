from app import app, db
from models.review import Review
import sys

def update_review(review_id=None, title=None, location=None, summary=None, content=None, image=None, author=None, is_published=True):
    """
    Update an existing review or create a new one if review_id is None.
    
    Args:
        review_id (int, optional): ID of the review to update. If None, a new review will be created.
        title (str): Title of the review.
        location (str): Location the review is about.
        summary (str): Short summary of the review.
        content (str): Full markdown content of the review.
        image (str, optional): URL to the review image.
        author (str, optional): Author of the review. Defaults to "Go Ask Marshall".
        is_published (bool, optional): Whether the review is published. Defaults to True.
    
    Returns:
        Review: The updated or created review.
    """
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        if review_id:
            # Update existing review
            review = Review.query.get(review_id)
            if not review:
                print(f"Error: Review with ID {review_id} not found.")
                return None
                
            if title:
                review.title = title
                review.slug = None  # Will be regenerated on save
            if location:
                review.location = location
            if summary:
                review.summary = summary
            if content:
                review.content = content
            if image:
                review.image = image
            if author:
                review.author = author
            
            review.is_published = is_published
            
            # Regenerate slug
            if title:
                from slugify import slugify
                review.slug = slugify(title)
                
            db.session.commit()
            print(f"Updated review: {review.title} with slug: {review.slug}")
            
        else:
            # Create new review
            if not title or not location or not summary or not content:
                print("Error: Title, location, summary, and content are required for new reviews.")
                return None
                
            # Set default image if none provided
            if not image:
                image = "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80"
                
            # Set default author if none provided
            if not author:
                author = "Go Ask Marshall"
                
            review = Review(
                title=title,
                location=location,
                summary=summary,
                content=content,
                image=image,
                author=author
            )
            review.is_published = is_published
            
            db.session.add(review)
            db.session.commit()
            print(f"Created review: {review.title} with slug: {review.slug}")
            
        return review

def list_reviews():
    """List all reviews in the database."""
    with app.app_context():
        reviews = Review.query.all()
        if not reviews:
            print("No reviews found in the database.")
            return
            
        print("\nExisting Reviews:")
        print("-" * 80)
        for review in reviews:
            status = "Published" if review.is_published else "Draft"
            print(f"ID: {review.id} | Title: {review.title} | Location: {review.location} | Status: {status}")
        print("-" * 80)

def delete_review(review_id):
    """Delete a review by ID."""
    with app.app_context():
        review = Review.query.get(review_id)
        if not review:
            print(f"Error: Review with ID {review_id} not found.")
            return False
            
        db.session.delete(review)
        db.session.commit()
        print(f"Deleted review: {review.title}")
        return True

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_reviews()
            
        elif command == "delete" and len(sys.argv) > 2:
            try:
                review_id = int(sys.argv[2])
                delete_review(review_id)
            except ValueError:
                print("Error: Review ID must be an integer.")
                
        else:
            print("Usage:")
            print("  python update_review.py list")
            print("  python update_review.py delete <review_id>")
            
    else:
        print("This script provides functions to update, create, list, and delete reviews.")
        print("Import and use the functions in your code, or run with 'list' or 'delete' commands.")
        print("\nExample usage:")
        print("  python update_review.py list")
        print("  python update_review.py delete 1")
        print("\nOr import in Python:")
        print("  from update_review import update_review, list_reviews, delete_review")

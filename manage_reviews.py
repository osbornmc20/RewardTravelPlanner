#!/usr/bin/env python3
"""
Review Management Script

This script provides a command-line interface for managing blog reviews in the travel rewards app.
It allows you to list, create, update, and delete reviews.

Usage:
  python manage_reviews.py list
  python manage_reviews.py create
  python manage_reviews.py update <review_id>
  python manage_reviews.py delete <review_id>
  python manage_reviews.py view <review_id>
"""

import sys
import os
from update_review import update_review, list_reviews, delete_review
from app import app, db
from models.review import Review

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, required=True, default=None):
    """Get user input with optional default value."""
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    else:
        while True:
            value = input(f"{prompt}: ").strip()
            if value or not required:
                return value
            print("This field is required.")

def get_multiline_input(prompt):
    """Get multiline input for content."""
    print(f"{prompt} (Enter a blank line to finish):")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)

def view_review(review_id):
    """View details of a specific review."""
    with app.app_context():
        review = Review.query.get(review_id)
        if not review:
            print(f"Error: Review with ID {review_id} not found.")
            return
        
        clear_screen()
        print(f"Review ID: {review.id}")
        print(f"Title: {review.title}")
        print(f"Slug: {review.slug}")
        print(f"Location: {review.location}")
        print(f"Author: {review.author}")
        print(f"Created: {review.created_at}")
        print(f"Updated: {review.updated_at}")
        print(f"Status: {'Published' if review.is_published else 'Draft'}")
        print(f"Image URL: {review.image}")
        print("\nSummary:")
        print(review.summary)
        print("\nContent:")
        print(review.content[:500] + "..." if len(review.content) > 500 else review.content)
        print("\n(Content truncated for display)")

def create_review():
    """Create a new review interactively."""
    clear_screen()
    print("=== Create New Review ===\n")
    
    title = get_input("Title")
    location = get_input("Location")
    author = get_input("Author", required=False, default="Go Ask Marshall")
    summary = get_input("Summary (brief description)")
    
    print("\nEnter content in Markdown format:")
    print("Tips: Use # for headings, ## for subheadings, * for bullet points")
    print("Enter a blank line to finish input\n")
    
    content = get_multiline_input("Content")
    
    image = get_input("Image URL", required=False, 
                     default="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80")
    
    is_published = get_input("Publish now? (y/n)", default="y").lower() == 'y'
    
    # Confirm before saving
    clear_screen()
    print("=== Review Preview ===\n")
    print(f"Title: {title}")
    print(f"Location: {location}")
    print(f"Author: {author}")
    print(f"Summary: {summary}")
    print(f"Image: {image}")
    print(f"Status: {'Published' if is_published else 'Draft'}")
    print(f"Content: (First 200 chars) {content[:200]}...")
    
    confirm = get_input("\nSave this review? (y/n)", default="y").lower()
    if confirm != 'y':
        print("Review creation cancelled.")
        return
    
    # Create the review
    review = update_review(
        title=title,
        location=location,
        summary=summary,
        content=content,
        image=image,
        author=author,
        is_published=is_published
    )
    
    if review:
        print(f"\nReview created successfully with ID: {review.id}")
        print(f"Access at: /reviews/{review.slug}")

def update_review_interactive(review_id):
    """Update an existing review interactively."""
    with app.app_context():
        review = Review.query.get(review_id)
        if not review:
            print(f"Error: Review with ID {review_id} not found.")
            return
        
        clear_screen()
        print(f"=== Update Review ID: {review.id} ===\n")
        print("(Press Enter to keep current values)\n")
        
        title = get_input(f"Title", required=False, default=review.title)
        location = get_input(f"Location", required=False, default=review.location)
        author = get_input(f"Author", required=False, default=review.author)
        summary = get_input(f"Summary", required=False, default=review.summary)
        
        print("\nCurrent content:")
        print(f"{review.content[:200]}...\n")
        update_content = get_input("Update content? (y/n)", default="n").lower() == 'y'
        
        if update_content:
            print("\nEnter new content in Markdown format:")
            print("Tips: Use # for headings, ## for subheadings, * for bullet points")
            print("Enter a blank line to finish input\n")
            content = get_multiline_input("Content")
        else:
            content = review.content
        
        image = get_input(f"Image URL", required=False, default=review.image)
        
        current_status = "Published" if review.is_published else "Draft"
        is_published = get_input(f"Status (Published/Draft)", default=current_status).lower() == "published"
        
        # Confirm before saving
        clear_screen()
        print("=== Review Update Preview ===\n")
        print(f"Title: {title}")
        print(f"Location: {location}")
        print(f"Author: {author}")
        print(f"Summary: {summary}")
        print(f"Image: {image}")
        print(f"Status: {'Published' if is_published else 'Draft'}")
        print(f"Content: (First 200 chars) {content[:200]}...")
        
        confirm = get_input("\nSave these changes? (y/n)", default="y").lower()
        if confirm != 'y':
            print("Update cancelled.")
            return
        
        # Update the review
        updated_review = update_review(
            review_id=review_id,
            title=title,
            location=location,
            summary=summary,
            content=content,
            image=image,
            author=author,
            is_published=is_published
        )
        
        if updated_review:
            print(f"\nReview updated successfully.")
            print(f"Access at: /reviews/{updated_review.slug}")

def delete_review_interactive(review_id):
    """Delete a review with confirmation."""
    with app.app_context():
        review = Review.query.get(review_id)
        if not review:
            print(f"Error: Review with ID {review_id} not found.")
            return
        
        print(f"\nYou are about to delete the review: '{review.title}'")
        confirm = get_input("Are you sure? This cannot be undone. (y/n)", default="n").lower()
        
        if confirm == 'y':
            delete_review(review_id)
            print("Review deleted successfully.")
        else:
            print("Deletion cancelled.")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_reviews()
    
    elif command == "create":
        create_review()
    
    elif command == "update" and len(sys.argv) > 2:
        try:
            review_id = int(sys.argv[2])
            update_review_interactive(review_id)
        except ValueError:
            print("Error: Review ID must be an integer.")
    
    elif command == "delete" and len(sys.argv) > 2:
        try:
            review_id = int(sys.argv[2])
            delete_review_interactive(review_id)
        except ValueError:
            print("Error: Review ID must be an integer.")
    
    elif command == "view" and len(sys.argv) > 2:
        try:
            review_id = int(sys.argv[2])
            view_review(review_id)
        except ValueError:
            print("Error: Review ID must be an integer.")
    
    else:
        print("Invalid command or missing arguments.")
        print(__doc__)

if __name__ == "__main__":
    main()

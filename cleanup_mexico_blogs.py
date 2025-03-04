from app import app, db
from models.review import Review
from update_review import update_review

with app.app_context():
    # 1. Delete the older blog post (ID 4)
    old_review = Review.query.get(4)
    if old_review:
        print(f"Deleting review: {old_review.title}")
        db.session.delete(old_review)
        db.session.commit()
        print("Review deleted successfully!")
    else:
        print("Review with ID 4 not found.")
    
    # 2. Update the image for the newer blog post with an actual Mexican beach image
    # This is a real image of Tulum, Mexico
    mexican_beach_image = "https://images.pexels.com/photos/1287460/pexels-photo-1287460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
    
    # Get the newest review (ID 5)
    new_review = Review.query.get(5)
    if new_review:
        print(f"\nUpdating image for: {new_review.title}")
        new_review.image = mexican_beach_image
        db.session.commit()
        print("Image updated successfully!")
        print(f"New image URL: {new_review.image}")
        print(f"To view: http://127.0.0.1:5041/reviews/{new_review.slug}")
    else:
        print("Review with ID 5 not found.")

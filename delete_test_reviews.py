from app import app, db
from models.review import Review

# Run within the application context
with app.app_context():
    def delete_review_by_title(title):
        """Delete a review by its title"""
        review = Review.query.filter_by(title=title).first()
        if review:
            print(f"Deleting review: {review.title}")
            db.session.delete(review)
            db.session.commit()
            return True
        else:
            print(f"Review with title '{title}' not found")
            return False

    # Delete the test reviews
    delete_review_by_title("Exploring Kyoto's Ancient Temples and Gardens")
    delete_review_by_title("Bali: Island of the Gods")

    print("\nRemaining reviews:")
    for review in Review.query.all():
        print(f"- {review.title}")

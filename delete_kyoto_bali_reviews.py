from app import app, db
from models.review import Review

# Run within the application context
with app.app_context():
    def delete_reviews_containing(keyword):
        """Delete reviews with titles containing the specified keyword"""
        reviews = Review.query.filter(Review.title.like(f'%{keyword}%')).all()
        if reviews:
            for review in reviews:
                print(f"Deleting review: {review.title}")
                db.session.delete(review)
            db.session.commit()
            return len(reviews)
        else:
            print(f"No reviews found containing '{keyword}'")
            return 0

    # Delete reviews containing "Kyoto" or "Bali"
    kyoto_count = delete_reviews_containing("Kyoto")
    bali_count = delete_reviews_containing("Bali")
    
    print(f"\nDeleted {kyoto_count} Kyoto reviews and {bali_count} Bali reviews")

    print("\nRemaining reviews:")
    for review in Review.query.all():
        print(f"- {review.title}")

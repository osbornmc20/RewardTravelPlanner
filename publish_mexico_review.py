from update_review import update_review

# Publish the Mexico beach hotels review (ID: 3)
updated_review = update_review(
    review_id=3,
    is_published=True
)

if updated_review:
    print(f"\nReview published successfully!")
    print(f"Title: {updated_review.title}")
    print(f"URL: /reviews/{updated_review.slug}")
    print(f"You can view it at: http://127.0.0.1:5041/reviews/{updated_review.slug}")

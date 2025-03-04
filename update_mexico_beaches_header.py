from update_review import update_review

# Update the Mexico hidden beaches review with a better header image
updated_review = update_review(
    review_id=4,  # ID of the Mexico beaches review
    image="https://images.unsplash.com/photo-1590080669911-3e65b0ba7461?ixlib=rb-1.2.1&auto=format&fit=crop&w=1500&q=80"
)

if updated_review:
    print(f"\nReview updated successfully!")
    print(f"Title: {updated_review.title}")
    print(f"New header image applied")
    print(f"To view: http://127.0.0.1:5041/reviews/{updated_review.slug}")

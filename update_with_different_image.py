from update_review import update_review

# Update the Mexico hidden beaches review with a different image source
updated_review = update_review(
    review_id=4,  # ID of the Mexico beaches review
    image="https://images.pexels.com/photos/1174732/pexels-photo-1174732.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
)

if updated_review:
    print(f"\nReview updated successfully!")
    print(f"Title: {updated_review.title}")
    print(f"New header image applied from Pexels")
    print(f"To view: http://127.0.0.1:5041/reviews/{updated_review.slug}")

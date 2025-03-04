from update_review import update_review

# Add the Mexico beach hotels review
new_review = update_review(
    title="Hidden Gem Beach Hotels in Mexico",
    location="Mexico",
    summary="Here are a few lesser-known beach hotels in Mexico worth checking out if you are in need of a place to relax without the crowds.",
    content="""# Hidden Gem Beach Hotels in Mexico

## Intro
Mexico is known for its stunning beaches, vibrant culture, and delicious cuisine. For those seeking unique and luxurious accommodations without breaking the bank, boutique beach hotels are the perfect option. We've tracked down five new amazing places to stay that will provide you with an unforgettable experience on your next trip!

## 1. Aldea Kuká - Isla Holbox, Quintana Roo
Nestled among lush greenery on the beautiful island of Isla Holbox, Aldea Kuká is an eco-friendly boutique hotel that focuses on sustainability. This hidden gem offers a serene atmosphere with its luxury villa design, perfect for a relaxing beach vacation.
- Link: aldeakuka.mx
- Activities: Explore the island by bicycle, and dont miss the chance to swim with whale sharks during their migration season (May to September).

## 2. Bruma Casa Hotel 8 - Baja California
Located in the heart of the Valle de Guadalupe wine region, Bruma Casa Hotel 8 offers a unique combination of beach and vineyard experiences. With its modern design and high-end amenities, this boutique hotel is perfect for those seeking a luxurious and intimate getaway.
- Booking Link: https://bruma.mx/
- Activities: Take a guided tour of the nearby vineyards, and enjoy a day of relaxation at the hotels spa facility.

## 3. Azulik - Tulum, Quintana Roo
Azulik, an eco-luxury beach resort in Tulum, offers guests a one-of-a-kind experience with its treehouse-like villas and breathtaking ocean views. This sustainable boutique hotel is perfect for travelers seeking a unique and luxurious escape.
- Booking Link: [Azulik](https://www.azulik.com/reservations/)
- Activities: Participate in a traditional Mayan healing ceremony at the hotels spa, and explore the ancient Mayan ruins of Tulum.

## 4. Zoa Hotel - Mazunte, Oaxaca
Situated on the Pacific coast of Oaxaca, Zoa Hotel offers a tranquil and intimate atmosphere for guests. With only five rooms, this boutique hotel guarantees personalized service and unmatched privacy.
- Booking Link: [Zoa Hotel](https://www.zoahotel.com/reservations/)
- Activities: Discover the nearby turtle sanctuary at La Ventanilla, and take a boat tour to observe dolphins and whales in their natural habitat.

## 5. Marea Beachfront Villas - Zihuatanejo, Guerrero
Marea Beachfront Villas offers guests a luxurious and secluded beach experience in Zihuatanejo. Each of the six villas boasts a private pool and direct beach access, providing the ultimate relaxation experience.
- Booking Link: [Marea Beachfront Villas](https://www.mareavillas.com/book/)
- Activities: Enjoy a private cooking class with a local chef, and try your hand at surfing with a professional instructor.

## Conclusion
These five new boutique beach hotels in Mexico offer travelers unique and luxurious accommodations without the hefty price tag. Book your stay now and experience the best of Mexico's beaches and culture. Happy travels!
""",
    image="https://images.unsplash.com/photo-1519046904884-53103b34b206?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
    author="Go Ask Marshall",
    is_published=False  # Save as draft
)

if new_review:
    print(f"\nReview created successfully!")
    print(f"Title: {new_review.title}")
    print(f"Slug: {new_review.slug}")
    print(f"Status: {'Published' if new_review.is_published else 'Draft'}")
    print(f"To view when published: /reviews/{new_review.slug}")

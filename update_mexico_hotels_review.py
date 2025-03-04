from update_review import update_review

# Update the Mexico beach hotels review with improved formatting and images
updated_review = update_review(
    review_id=3,
    title="Hidden Gem Beach Hotels in Mexico",
    location="Mexico",
    summary="Here are a few lesser-known beach hotels in Mexico worth checking out if you are in need of a place to relax without the crowds.",
    content="""# Hidden Gem Beach Hotels in Mexico

## Intro
Mexico is known for its stunning beaches, vibrant culture, and delicious cuisine. For those seeking unique and luxurious accommodations without breaking the bank, boutique beach hotels are the perfect option. We've tracked down five new amazing places to stay that will provide you with an unforgettable experience on your next trip!

## 1. Aldea Kuká - Isla Holbox, Quintana Roo

![Aldea Kuká](https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

Nestled among lush greenery on the beautiful island of Isla Holbox, Aldea Kuká is an eco-friendly boutique hotel that focuses on sustainability. This hidden gem offers a serene atmosphere with its luxury villa design, perfect for a relaxing beach vacation.

### Activities
- Explore the island by bicycle
- Don't miss the chance to swim with whale sharks during their migration season (May to September)
- Take a kayak tour through the mangroves

### Booking Information
[Visit Aldea Kuká Website](https://aldeakuka.mx)

## 2. Bruma Casa Hotel 8 - Baja California

![Bruma Casa Hotel](https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

Located in the heart of the Valle de Guadalupe wine region, Bruma Casa Hotel 8 offers a unique combination of beach and vineyard experiences. With its modern design and high-end amenities, this boutique hotel is perfect for those seeking a luxurious and intimate getaway.

### Activities
- Take a guided tour of the nearby vineyards
- Enjoy a day of relaxation at the hotel's spa facility
- Participate in wine tasting sessions with local experts

### Booking Information
[Visit Bruma Casa Hotel Website](https://bruma.mx/)

## 3. Azulik - Tulum, Quintana Roo

![Azulik Tulum](https://images.unsplash.com/photo-1535913989690-f90e1c2d4cfa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

Azulik, an eco-luxury beach resort in Tulum, offers guests a one-of-a-kind experience with its treehouse-like villas and breathtaking ocean views. This sustainable boutique hotel is perfect for travelers seeking a unique and luxurious escape.

### Activities
- Participate in a traditional Mayan healing ceremony at the hotel's spa
- Explore the ancient Mayan ruins of Tulum
- Practice yoga at the hotel's oceanfront yoga studio

### Booking Information
[Visit Azulik Website](https://www.azulik.com/reservations/)

## 4. Zoa Hotel - Mazunte, Oaxaca

![Zoa Hotel](https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

Situated on the Pacific coast of Oaxaca, Zoa Hotel offers a tranquil and intimate atmosphere for guests. With only five rooms, this boutique hotel guarantees personalized service and unmatched privacy.

### Activities
- Discover the nearby turtle sanctuary at La Ventanilla
- Take a boat tour to observe dolphins and whales in their natural habitat
- Enjoy sunset meditation sessions on the hotel's private beach

### Booking Information
[Visit Zoa Hotel Website](https://www.zoahotel.com/reservations/)

## 5. Marea Beachfront Villas - Zihuatanejo, Guerrero

![Marea Beachfront Villas](https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)

Marea Beachfront Villas offers guests a luxurious and secluded beach experience in Zihuatanejo. Each of the six villas boasts a private pool and direct beach access, providing the ultimate relaxation experience.

### Activities
- Enjoy a private cooking class with a local chef
- Try your hand at surfing with a professional instructor
- Explore the local markets and artisan shops in Zihuatanejo

### Booking Information
[Visit Marea Beachfront Villas Website](https://www.mareavillas.com/book/)

## Conclusion
These five new boutique beach hotels in Mexico offer travelers unique and luxurious accommodations without the hefty price tag. Book your stay now and experience the best of Mexico's beaches and culture. Happy travels!
""",
    image="https://images.unsplash.com/photo-1519046904884-53103b34b206?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
    author="Go Ask Marshall",
    is_published=True
)

if updated_review:
    print(f"\nReview updated successfully!")
    print(f"Title: {updated_review.title}")
    print(f"URL: /reviews/{updated_review.slug}")
    print(f"You can view it at: http://127.0.0.1:5041/reviews/{updated_review.slug}")

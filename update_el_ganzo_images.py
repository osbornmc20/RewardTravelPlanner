from update_review import update_review

# Update the Hotel El Ganzo review with better images
updated_review = update_review(
    review_id=6,  # ID of the Hotel El Ganzo review
    content="""# Hotel El Ganzo: A Boutique Luxury Experience in San Jose del Cabo

## Introduction
Located in the peaceful surroundings of San Jose Del Cabo, Hotel El Ganzo offers more than just a common getaway. It provides an escape from the busy and overcrowded resort areas. If you're looking for a sophisticated retreat with a little bit of privacy, this boutique hotel delivers an experience that's both personal and refreshing. It just so happens to be one of our favorite hotels in Cabo, and where we got married! Read below to learn more about this amazing property.

## A Sanctuary by the Sea

![Hotel El Ganzo Exterior](https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/2e/5a/9e/hotel-el-ganzo.jpg?w=1200&h=-1&s=1)

From the moment you step into the lobby of Hotel El Ganzo, you are greeted by an ambiance that marries contemporary art with a serene oceanfront setting. The hotel's commitment to supporting local arts is apparent in every corner. Various works are on display around the lobby, and the entire hotel which get updated throughout the year.

### Activities
- Explore the hotel's art installations and rotating exhibits
- Relax by the stunning rooftop infinity pool
- Enjoy exclusive access to the hotel's private beach club
- Listen to live music performances from visiting artists

### Booking Information
[Book at Hotel El Ganzo](https://www.elganzo.com/reservations)

## Amenities Galore

![Rooftop Pool](https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/2e/5b/1e/rooftop-infinity-pool.jpg?w=1200&h=-1&s=1)

Hotel El Ganzo prides itself on its well-curated selection of amenities designed to cater to every guest's needs. The pièce de résistance is undoubtedly the amazing rooftop pool, offering panoramic views of the azure Sea of Cortez. It's a perfect vantage point for both sunrise enthusiasts and sunset romantics. 

Additionally, guests have exclusive access to El Ganzo's own swimmable beach – a rarity in this region known for its rough waters. The privacy afforded by its location, not being flanked by other resorts, adds to the sense of exclusive tranquility.

Every room at Hotel El Ganzo boasts an oceanfront view, ensuring that guests can wake up to the sight and sounds of waves gently kissing the shore. This feature alone sets El Ganzo apart, as it guarantees all who stay here are enveloped in coastal beauty throughout their visit.

### Activities
- Swim in the stunning rooftop infinity pool with panoramic views
- Relax at the private beach club with swimmable waters
- Enjoy the spa with treatments incorporating local ingredients
- Work out in the fitness center with ocean views

### Booking Information
[View Room Options](https://www.elganzo.com/rooms)

## Culinary Experiences

![Beach Club Dining](https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/2e/5b/0e/beach-club.jpg?w=1200&h=-1&s=1)

Hotel El Ganzo offers an array of dining options on-site from super casual tacos to formal candle-lit dinners. You can't go wrong with any of them, but the simple menu of seafood & tacos at the Beach Club is a highlight for us.

**The Ganzo De Playa**: Enjoy your meal with sand between your toes and the sound of waves in the background. Fresh Ceviches, yummy tacos, and incredible views await.

**The Rooftop**: The rooftop restaurant offers a variety of options from seafood to burgers while soaking up panoramic views of the Sea of Cortez.

**El Restaurante**: This is the main restaurant, off the lobby, where they serve breakfast, lunch, and a more formal dinner. We love the breakfast options, especially the weekend buffet, but are not always a fan of the dinner menu. I've felt that the ingredient combinations are a bit strange and we generally avoid eating here at night. *Pro Tip - Go the the restaurant at La Marina Inn across the street for an amazing dinner with live music!*

**Taco Taco Ganzo**: This taco truck is a new addition that was added to the property within the last year or two. Open late on weekends, it offers guests and locals a chance for an authentic Mexican street taco without leaving the property.

### Activities
- Enjoy fresh seafood at the beachfront restaurant
- Sample creative cocktails at the rooftop bar
- Experience authentic Mexican street tacos at Taco Taco Ganzo
- Take a short walk to nearby La Marina Inn for dinner alternatives

### Booking Information
[Make Dining Reservations](https://www.elganzo.com/dining)

## The Artistic Atmosphere

![Hotel Lobby Art](https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/2e/5a/b0/lobby.jpg?w=1200&h=-1&s=1)

This isn't your standard beach resort; it's a living, breathing gallery. Every corner of the hotel is adorned with unique artwork and installations by local and international artists. You can wander through the corridors and stumble upon a groundbreaking piece of contemporary art, making your stay not only relaxing but culturally enriching.

The Underground Recording Studio: Yes, you read that right! Hotel El Ganzo houses an underground recording studio where musicians from around the globe have recorded. Who knows? You might share an elevator with a Grammy award-winning artist.

The Ganzo Downstairs: This isn't just another hotel bar, it's a destination in itself. With live music performances and an impressive cocktail menu that changes with the seasons, The Ganzo Downstairs is the perfect spot to let your hair down and dance the night away.

### Activities
- Tour the hotel's art collection with staff guides
- Check the schedule for live music performances
- Visit the underground recording studio (when available)
- Attend special art events and music showcases

### Booking Information
[View Upcoming Events](https://www.elganzo.com/events)

## Things That Could Improve

While Hotel El Ganzo offers an exceptional experience, there are a few areas where improvements could be made:

1. **Consistent Customer Service**: While most of the staff provide excellent service, there can be occasional inconsistencies in the level of attention and care provided.

2. **Dinner Menu Variety**: Though the food quality is excellent, the dinner menu at El Restaurante could benefit from more diverse options and flavors that appeal to a wider range of palates.

3. **Location**: The hotel's secluded location is part of its charm, but it does mean there aren't many attractions within walking distance. Guests should plan to rent a car or use taxis for exploring beyond the property.

## Conclusion

With everything considered – from its stunning location and impressive amenities to its few shortcomings – Hotel El Ganzo deserves an 8 out of 10 rating. It stands as a beacon for those seeking luxury without ostentation and offers a unique blend of artistry, relaxation, and personal service. 

For travelers looking for an upscale retreat with character and charm away from crowded tourist spots, Hotel El Ganzo will not disappoint. Whether you're celebrating a special occasion (like we did with our wedding), seeking a creative inspiration, or simply wanting a peaceful getaway, this boutique hotel delivers an experience that's both memorable and distinctive.
""",
    image="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/2e/5a/9e/hotel-el-ganzo.jpg?w=1200&h=-1&s=1"
)

if updated_review:
    print(f"\nReview updated successfully!")
    print(f"Title: {updated_review.title}")
    print(f"Images updated with actual Hotel El Ganzo photos")
    print(f"To view: http://127.0.0.1:5041/reviews/{updated_review.slug}")

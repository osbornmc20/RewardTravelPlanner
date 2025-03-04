from app import app, db
from models.review import Review

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if the review already exists
    existing_review = Review.query.filter_by(title='The Hidden Gems of Kyoto: Beyond the Tourist Trail').first()
    
    if not existing_review:
        # Create a sample review
        review = Review(
            title='The Hidden Gems of Kyoto: Beyond the Tourist Trail',
            location='Kyoto, Japan',
            summary='Discover the lesser-known temples, gardens, and neighborhoods that make Kyoto truly special. This guide takes you away from the crowds to experience authentic Japanese culture and tranquility.',
            content='''# The Hidden Gems of Kyoto: Beyond the Tourist Trail

Kyoto, the cultural heart of Japan, is known for its iconic temples, shrines, and gardens. While Kinkaku-ji (Golden Pavilion) and Fushimi Inari Shrine are must-see attractions, the true magic of Kyoto lies in its hidden corners and lesser-known spots.

## Escape the Crowds at Daitoku-ji Temple Complex

While tourists flock to Kinkaku-ji and Ryoan-ji, the Daitoku-ji temple complex offers a peaceful alternative. This collection of Zen temples and gardens provides a serene escape from the crowds. The sub-temples Zuiho-in and Daisen-in feature some of the most exquisite rock gardens in Kyoto, yet they receive only a fraction of the visitors of their more famous counterparts.

## Explore the Philosopher's Path in Off-Season

The Philosopher's Path is a stone walkway that follows a canal lined with cherry trees. While it's extremely popular during cherry blossom season, visiting during autumn or winter reveals a completely different atmosphere. The path connects several temples worth exploring, including the often-overlooked Honen-in with its moss-covered gate and seasonal garden displays.

## Discover Kyoto's Traditional Crafts

Kyoto has been the center of traditional Japanese crafts for centuries. Visit the Nishijin Textile Center to learn about kimono weaving, or explore the small workshops in the Higashiyama district where artisans create everything from woodblock prints to lacquerware. Many offer hands-on experiences where you can try your hand at these ancient crafts.

## Wander Through Local Food Markets

Nishiki Market may be in all the guidebooks, but locals prefer the smaller neighborhood markets. Explore Fushimi Market or the morning market at Kitano Tenmangu Shrine for a more authentic experience. These markets offer seasonal specialties and local delicacies without the tourist markup.

## Stay in a Traditional Machiya

Instead of a hotel, consider staying in a machiya, a traditional wooden townhouse. Many have been beautifully restored while maintaining their historical character. These accommodations offer a glimpse into traditional Japanese domestic life and are often located in residential neighborhoods, giving you a more authentic experience of Kyoto.

## Experience Tea Ceremony in a Private Setting

While there are many places offering tea ceremony experiences for tourists, seek out smaller, less commercial venues. Camellia Tea Ceremony offers intimate sessions in English, or for a truly special experience, arrange a private ceremony at Daitoku-ji's Kohoan temple (advance reservations required).

## Conclusion

The true beauty of Kyoto reveals itself when you step away from the well-trodden tourist path. By exploring these hidden gems, you'll discover the authentic charm and tranquility that has made Kyoto Japan's cultural capital for over a millennium.''',
            image='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'
        )
        
        # Add to database and commit
        db.session.add(review)
        db.session.commit()
        
        print(f'Created review: {review.title} with slug: {review.slug}')
    else:
        print(f'Review already exists: {existing_review.title} with slug: {existing_review.slug}')

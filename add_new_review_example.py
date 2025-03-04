from update_review import update_review, list_reviews

# First, let's list existing reviews
list_reviews()

# Now, let's add a new review
new_review = update_review(
    title="Exploring the Hidden Beaches of Bali",
    location="Bali, Indonesia",
    summary="Discover secluded beaches away from the tourist crowds in Bali. This guide reveals pristine shorelines, secret coves, and local beach spots that offer tranquility and natural beauty.",
    content="""# Exploring the Hidden Beaches of Bali

Bali is famous for its beautiful beaches, but the most popular ones like Kuta, Seminyak, and Nusa Dua can get extremely crowded. For travelers seeking tranquility and untouched natural beauty, Bali offers numerous hidden beaches that remain relatively unknown to most tourists.

## Bias Tugel Beach

Located near Padang Bai in East Bali, Bias Tugel (also known as Pantai Kecil or "Little Beach") requires a short 500-meter hike down a rocky path. The effort is rewarded with a pristine white sand beach, crystal clear waters, and far fewer visitors than nearby beaches. The small bay is protected by rocky outcrops, creating calm waters perfect for swimming and snorkeling.

## Green Bowl Beach

At the southern tip of Bali on the Bukit Peninsula, Green Bowl Beach is named for the green algae that covers the rock formations at low tide. Reaching this beach requires descending approximately 300 steps, which deters many tourists. The beach is home to two large limestone caves that provide shade and shelter, and the waters are excellent for snorkeling with abundant marine life.

## Nyang Nyang Beach

One of Bali's most secluded beaches, Nyang Nyang in Uluwatu requires a 20-minute trek through fields and down a steep cliff path. The beach stretches for nearly 1.5 kilometers of white sand, with virtually no development aside from a couple of small local vendors selling coconuts and drinks. The powerful waves make it popular with experienced surfers, while others can enjoy the vast, empty stretches of sand.

## Gunung Payung Beach

Hidden below the Gunung Payung temple in South Kuta, this beach requires a descent of about 300 steps. The beach features dramatic limestone cliffs, soft white sand, and beautiful coral reefs just offshore. The challenging access means you might have the entire beach to yourself, especially on weekdays.

## Pasir Putih (White Sand Beach)

Located in East Bali near Candidasa, Pasir Putih (literally "White Sand") is a stunning contrast to the black volcanic beaches common in the area. Nestled between two headlands and backed by coconut groves, this beach has a few simple warungs (local restaurants) serving fresh seafood. The calm waters are perfect for swimming, and you can rent traditional jukung fishing boats for exploring the coastline.

## Tips for Visiting Hidden Beaches

1. **Bring supplies**: Most hidden beaches have limited or no facilities, so bring water, snacks, and sun protection.
2. **Tide awareness**: Some beaches become very narrow or disappear completely at high tide. Check tide schedules before visiting.
3. **Transportation**: Rent a scooter or hire a driver for the day, as most hidden beaches are not accessible by public transportation.
4. **Respect the environment**: Take all trash with you and avoid disturbing the natural ecosystem.
5. **Safety first**: Many hidden beaches don't have lifeguards, so swim with caution and be aware of potential rip currents.

## Conclusion

Bali's hidden beaches offer a glimpse of the island's natural beauty without the crowds that characterize its more famous shores. The extra effort required to reach these secluded spots is always rewarded with pristine environments, peaceful atmospheres, and authentic experiences that connect you with the true spirit of Bali.
""",
    image="https://images.unsplash.com/photo-1537996194471-e657df975ab4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
    author="Go Ask Marshall",
    is_published=True
)

# List reviews again to see the new addition
if new_review:
    print("\nUpdated review list:")
    list_reviews()

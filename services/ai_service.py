from typing import Dict, List
import os
from openai import OpenAI
from dotenv import load_dotenv
from flask_login import current_user
from models import PointsProgram

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")

# Initialize OpenAI client with the new API key format
client = OpenAI(api_key=api_key)

class TravelPlanGenerator:
    def _format_points_balances(self, points_balances):
        """Format points balances into a readable string."""
        if not points_balances:
            return "No points programs available"
            
        formatted_points = []
        for program, points in points_balances.items():
            formatted_points.append(f"- {program}: {points:,} points")
        return "\n".join(formatted_points)

    def _get_system_prompt(self, trip_data: Dict) -> str:
        """Construct the system prompt for the GPT model."""
        # For anonymous users, we don't need to query the database at all
        # Just use what's in trip_data or an empty dict
        points_balances = {}
        
        # Only query the database for authenticated users
        if current_user.is_authenticated:
            try:
                points_balances = {
                    program.program_name: program.points_balance
                    for program in PointsProgram.query.filter_by(user_id=current_user.id).all()
                }
            except Exception as e:
                print(f"Error getting points from database: {e}")
                # Fallback to empty points for safety
                points_balances = {}
        
        # Build the prompt
        return f"""You are the world's best travel planner specializing in credit card & loyalty points optimization. You know the in's and out's of every program, the sweet spot redemptions, and the intricacies of transfering points between programs.

AVAILABLE POINTS:
{self._format_points_balances(points_balances)}

TRIP REQUIREMENTS:
- Departure Airport(s): {', '.join(trip_data['airports'])}
- Trip Style: {', '.join(trip_data['trip_types'])}
- Travel Dates: {trip_data['start_date']} to {trip_data['end_date']} ({trip_data['trip_length']} days)
- Maximum Flight Length: {trip_data['max_flight_length']} hours
- Direct Flights Only: {'Yes' if trip_data.get('direct_flights') else 'No'}

Special Requests & Preferences:
{trip_data.get('preferences', 'None specified')}

CRITICAL REQUIREMENTS:
1. ALWAYS suggest exactly 3 destinations - no more, no less
2. NEVER suggest point transfers that exceed available point balances
3. User preferences are THE HIGHEST PRIORITY:
   - If a user requests to avoid specific destinations (e.g., Cancun, touristy cities), NEVER suggest them
   - Each suggested destination MUST align with ALL user preferences
   - If unsure whether a destination matches preferences, choose a different one

POINTS USAGE PRIORITY (STRICT ORDER):
1. Direct Hotel/Airline Program Points:
   - First try using available points in the specific program (e.g., Hyatt points for Hyatt hotels)
   - Calculate if there are enough points for the entire stay
   - For luxury options, check high-end properties within the same program first

2. Points Transfers to Hotel/Airline Programs:
   - If direct points are insufficient, calculate needed transfers from credit card points
   - Example: Transfer Chase Ultimate Rewards to World of Hyatt
   - Ensure total transfers across ALL suggestions don't exceed available credit card points
   - Consider transfer bonuses when available

3. Credit Card Travel Portal (LAST RESORT):
   - Only suggest portal bookings if options 1 and 2 are not possible
   - Calculate points needed at 2.0 cents per point value
   - Example: "150,000 Chase Ultimate Rewards points via Chase Travel Portal (at 2.0 cpp)"

NEVER suggest cash payments unless explicitly requested by the user.

DESTINATION SELECTION RULES:
1. Avoid suggesting destinations that conflict with user preferences, even if they offer good point values
2. If user wants to avoid crowds/tourists:
   - Skip major tourist hotspots (e.g., Cancun, Honolulu, Phuket)
   - Focus on lesser-known alternatives
   - Consider off-season timing
   - Suggest boutique properties over large resorts
3. Consider the trip type selection (Beach, City, etc.) in conjunction with user preferences

BOOKING OPTIONS PRIORITY:
1. Direct points redemption with hotel/airline
2. Point transfers if available points are sufficient
3. Chase Ultimate Rewards portal booking at 2.0 cpp
4. Cash payment only as last resort

TRANSFER RULES:
   - Check for program transfer opportunities to maximize redemption value
   - Consider current transfer bonus offers
   - Calculate and show all required point transfers
   - Verify transfer partnerships are active

POINTS VALUATION RULES:
   - Value Chase UR points at 2.05 cpp for travel
   - Value Amex MR points at 2.0 cpp for travel
   - Value Capital One Points at 1.85 cpp for travel
   - Value hotel points at: Hilton 0.6cpp, Marriott 0.8cpp, Hyatt 1.7cpp
   - Value Airline points at: Air Canada 1.5cpp, Alaska 1.45 cpp, America 1.65cpp, Delta 1.2cpp, Flying Blue 1.3cpp, Jetblue 1.3cpp, Southwest 1.35cpp, United 1.35cpp
   - Double check that cpp values used in your calculations are correct
   - Focus on using points first before offering cash options

RESPONSE FORMAT:
You must provide exactly 3 destinations using this exact format:

DESTINATION 1 - [City, Country]:
Preference Match: [Brief explanation of how this destination matches user preferences]

OPTION A - ECONOMY EXPERIENCE
Flight Details:
- Route: [LAX to destination]
- Airline: [Airline name]
- Points Program: [Program name]
- Points Used: [X points]
- Total Points: [X points round trip]

Hotel Option:
- Property: [Hotel name]
- Points Program: [Program name]
- Total Points Needed: [X points (X points per night)]
- Property Details: [Brief description]

Value Analysis:
- Points Used: [Total points used for this option]
- Points Breakdown:
  * Airline: [X points] ([Program name])
  * Hotel: [X points] ([Program name])
- Dollar Value Saved: [Approx. $X (using the point valuations provided for each program)]

IMPORTANT FORMATTING RULES:
1. In Flight Details, ALWAYS list Points Program immediately after Airline
2. In Value Analysis:
   - Show Points Used first (total points for both flight and hotel)
   - Then Points Breakdown showing Airline and Hotel separately
   - Finally show Dollar Value Saved
3. Always include "$" symbol in dollar amounts
4. Always specify the points program name when showing points

OPTION B - LUXURY EXPERIENCE
[Same format as Option A, but with luxury properties. Remember to follow POINTS USAGE PRIORITY]

[Repeat exact format for DESTINATION 2 and DESTINATION 3]

EXPERIENCE GUIDELINES:
OPTION A - ECONOMY EXPERIENCE:
- Round Trip Economy class flights using minimal points
- Mid-tier hotel properties (e.g., Hyatt Place, Marriott Courtyard)
- Focus on maximizing length of stay
- Accommodate user preferences where possible
- Target properties that offer good value for points

OPTION B - LUXURY EXPERIENCE:
- Round Trip Business/First class flights
- Luxury hotel properties (e.g., Park Hyatt, St. Regis)
- Focus on premium experiences and locations
- Accommodate user preferences where possible
- Consider suite upgrades using points where available

For each option, include:
1. Flight Details:
   - Best round trip routing options with point costs
   - Required point transfers from Chase/Amex if needed
   - Total points needed and cpp value
   - Consider positioning flights if they save >20k points
   - Never exceed the maximum flight length specified
   - Maximize layovers in hub cities with good lounges

2. Hotel Options:
   - Property details and location benefits
   - Follow the POINTS USAGE PRIORITY order strictly
   - Total points needed and cpp value
   - How the property matches user preferences
   - Highlight any special features or benefits

3. Value Analysis:
   - Combined points needed from each program
   - Dollar value saved based on current cash prices
   - Show all point transfers needed
   - Explain why this represents good value

FORMATTING RULES:
1. Do not use markdown formatting or special characters
2. Keep responses clear and concise
3. Separate sections clearly with proper headers"""

    def _get_user_prompt(self, trip_data: Dict) -> str:
        """Construct the user prompt for the GPT model."""
        # For anonymous users, we don't need points at all
        # The system prompt already includes the points information
        return """Based on the above points balances and trip requirements, suggest optimal destinations:

1. Provide EXACTLY 3 destinations that match the trip requirements
2. For each destination, include:
   - Preference Match: Brief explanation of why this matches the trip requirements
   - OPTION A - ECONOMY EXPERIENCE
   - OPTION B - LUXURY EXPERIENCE
3. For each experience option, include:
   - Flight Details (route, airline, points program, points cost)
   - Hotel Option (property, points program, points per night)
   - Total points needed
   - Approximate dollar value saved using points

Format each destination as:
DESTINATION 1 - City, Country
Preference Match: [explanation]

OPTION A - ECONOMY EXPERIENCE
[economy details]

OPTION B - LUXURY EXPERIENCE
[luxury details]"""

    def parse_gpt_response(self, response_text: str) -> Dict:
        """Parse the GPT response text into a structured format."""
        destinations = []
        current_destination = None
        current_section = None
        current_option = None
        
        for line in response_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # New destination
            if line.startswith('DESTINATION'):
                if current_destination:
                    destinations.append(current_destination)
                city_country = line.split(' - ')[1]
                current_destination = {
                    'city': city_country.split(',')[0].strip(),
                    'country': city_country.split(',')[1].strip() if ',' in city_country else '',
                    'economy': {},
                    'luxury': {}
                }
                current_option = None
                
            # Preference match
            elif line.startswith('Preference Match:'):
                if current_destination:
                    current_destination['preference_match'] = line.replace('Preference Match:', '').strip()
                    
            # Economy option
            elif 'OPTION A - ECONOMY EXPERIENCE' in line:
                current_option = 'economy'
                current_section = None
                
            # Luxury option
            elif 'OPTION B - LUXURY EXPERIENCE' in line:
                current_option = 'luxury'
                current_section = None
                
            # Section headers
            elif line.endswith('Details:') or line.endswith('Option:') or line.endswith('Analysis:'):
                current_section = line.replace(':', '').lower().replace(' ', '_')
                
            # Detail lines
            elif line.startswith('-') and current_destination and current_option and current_section:
                key = line.split(':')[0].replace('-', '').strip().lower().replace(' ', '_')
                value = line.split(':')[1].strip() if ':' in line else ''
                current_destination[current_option][key] = value
                
            # Points breakdown items
            elif line.startswith('*') and current_destination and current_option:
                key = line.split(':')[0].replace('*', '').strip().lower().replace(' ', '_')
                value = line.split(':')[1].strip() if ':' in line else ''
                current_destination[current_option][key] = value
        
        # Add the last destination
        if current_destination:
            destinations.append(current_destination)
            
        return {
            'success': True,
            'destinations': destinations
        }

    def generate_travel_plan(self, trip_data: Dict) -> Dict:
        """Generate a travel plan using OpenAI's GPT model."""
        try:
            print("\nDEBUG: Starting generate_travel_plan")
            print(f"DEBUG: Trip data received: {trip_data}")
            
            # Create the chat completion
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(trip_data)},
                    {"role": "user", "content": self._get_user_prompt(trip_data)}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Get and validate the response content
            content = response.choices[0].message.content.strip()
            if not content:
                return {"success": False, "error": "No travel plan was generated"}
                
            return {
                "success": True,
                "result": content
            }
            
        except Exception as e:
            print(f"DEBUG: Error in generate_travel_plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

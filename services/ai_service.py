from typing import Dict, List
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

class TripValidationError(Exception):
    """Custom exception for trip validation errors."""
    pass

from flask_login import current_user
from models import PointsProgram
from flask import current_app

# Load environment variables from .env file
load_dotenv()

class TravelPlanGenerator:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=api_key)
        
    def _get_system_prompt(self, trip_data: Dict) -> str:
        """Construct the system prompt for the GPT model."""
        # Format must be exact for frontend parsing
        points_balances = {}
        
        # Get points balances from database for authenticated users
        if current_user.is_authenticated:
            try:
                points_balances = {
                    program.program_name: program.points_balance
                    for program in PointsProgram.query.filter_by(user_id=current_user.id).all()
                }
            except Exception as e:
                print(f"Error getting points from database: {e}")
                points_balances = {}
        # Get points balances from trip data for anonymous users
        else:
            try:
                points_balances = {
                    program['program_name']: program['points_balance']
                    for program in trip_data.get('points_programs', [])
                }
            except Exception as e:
                print(f"Error getting points from trip data: {e}")
                points_balances = {}
                
        special_requests = trip_data.get('preferences', 'None specified').strip()
        special_requests_emphasis = f"""
SPECIAL REQUESTS:
{special_requests}

These special requests must be followed for all destination suggestions:
- If specific regions/countries/cities are requested, only suggest matching destinations
- If certain places are excluded, do not suggest them
- All destinations must satisfy every special request
"""

        return f"""You are an expert travel planner specializing in credit card & loyalty points optimization. Generate travel recommendations based on:

AVAILABLE POINTS:
{self._format_points_balances(points_balances)}

{special_requests_emphasis}

TRIP REQUIREMENTS:
- Departure Airport(s): {', '.join(trip_data['airports'])}
- Trip Style: {', '.join(trip_data['trip_types'])}
- Preferred Travel Time: {trip_data['travel_months']} ({trip_data['trip_length']} days)
- Maximum Flight Length: {trip_data['max_flight_length']} hours
- Direct Flights Only: {'Yes' if trip_data.get('direct_flights') else 'No'}

REQUIREMENTS:
1. All point calculations must be accurate and within available balances
2. Economy and luxury options must be different
3. Luxury options must include premium economy, business or first class flights
4. Fare Type must be clearly specified for all flights
5. Show exactly 2 destinations that match all special requests
6. All point calculations must be for round trip flights per person
7. Consider seasonal factors for each destination:
    - Weather patterns and best times to visit
    - Peak vs. off-peak travel seasons
    - Local festivals and events
    - Typical award availability patterns

POINTS USAGE PRIORITY (STRICT ORDER):
1. Direct Hotel/Airline Program Points
   - Use points directly in the specific program first
   - Calculate if enough points for entire stay/flight
2. Points Transfers to Programs
   - Transfer credit card points if direct points insufficient
   - ONLY use verified transfer partnerships below
   - Consider current transfer bonuses
3. Credit Card Travel Portal (LAST RESORT)
   - Only if options 1 and 2 not possible
   - Calculate at 2.0 cents per point value

VERIFIED TRANSFER PARTNERSHIPS (STRICT - DO NOT SUGGEST OTHERS):
Chase Ultimate Rewards:
- Airlines: United, Southwest, Air Canada, British Airways, Air France/KLM, Virgin Atlantic, Emirates, Singapore Airlines, Iberia, Aer Lingus
- Hotels: Hyatt, IHG, Marriott

Amex Membership Rewards:
- Airlines: Delta, Air Canada, British Airways, Air France/KLM, Emirates, JetBlue, Singapore Airlines, Virgin Atlantic, ANA, Cathay Pacific, Etihad, Hawaiian
- Hotels: Hilton, Marriott, Choice

Capital One:
- Airlines: Air Canada, Air France/KLM, British Airways, Emirates, Singapore Airlines, Turkish Airlines, Virgin Red, TAP Air Portugal
- Hotels: Wyndham, Choice

Citi ThankYou:
- Airlines: Air France/KLM, Emirates, Singapore Airlines, Virgin Atlantic, Turkish Airlines, Qatar Airways, Etihad, EVA Air
- Hotels: Choice

POINT VALUES (cpp):
- Credit Cards: Chase 2.05, Amex 2.0, Capital One 1.85
- Hotels: Hilton 0.6, Marriott 0.8, Hyatt 1.7
- Airlines: Air Canada 1.5, Alaska 1.45, American 1.65, Delta 1.2, Flying Blue 1.3, JetBlue 1.3, Southwest 1.35, United 1.35

START YOUR RESPONSE WITH THE FOLLOWING FORMAT EXACTLY:
DESTINATION 1 - [City, Country]:

DESTINATION SUMMARY:
[2-3 sentences about why this destination is an excellent match for the requested travel time and trip style]

Why We Recommend This Destination:

1. Requirements Match:

✓ [Requirement 1]: [Brief explanation]

✓ [Requirement 2]: [Brief explanation]

✓ [Requirement 3]: [Brief explanation]


2. Seasonal Analysis:
   🌤️ Weather Conditions:
      • [Current season's weather patterns]
      • [Why it's ideal for travel]
   
   🎉 Local Highlights:
      • [Key festivals and events]
      • [Special seasonal activities]



<br><br>
3. Points Optimization:
   🎯 Award Availability:
      • [Current booking patterns]
      • [Best booking windows]
   
   💰 Value Opportunities:
      • [Transfer bonuses or sweet spots]
      • [Special redemption options]

OPTION A - ECONOMY EXPERIENCE
Flight Details:
- <b>Route</b>: [Airport to destination]
- <b>Airline</b>: [Airline name]
- <b>Points Program</b>: [Program name]
- <b>Points Used</b>: [X points RT per person]
- <b>Fare Class</b>: Economy (Main Cabin)

Hotel Option:
- <b>Property</b>: [Hotel name]
- <b>Points Program</b>: [Program name]
- <b>Total Points Needed</b>: [X points (X points per night)]
- <b>Property Details</b>: [Brief description]

Value Analysis:
- <b>Total Points Used</b>: [Total points used]
- <b>Airline</b>: [X points] ([Program name])
- <b>Hotel</b>: [X points] ([Program name])
- <b>Dollar Value Saved</b>: [Approx. $X]

OPTION B - LUXURY EXPERIENCE
Flight Details:
- Route: [Airport to destination]
- Airline: [Airline name]
- Points Program: [Program name]
- <b>Points Used</b>: [X points round trip per person]
- <b>Fare Class</b>: [Premium Economy/Business/First] (specify exact cabin)
- Award Availability: [Typical availability for these months]

Hotel Option:
- Property: [Luxury hotel name]
- Points Program: [Program name]
- Total Points Needed: [X points (X points per night)]
- Property Details: [Brief luxury description]

Value Analysis:
- <b>Total Points Used</b>: [Total points used]
- <b>Airline</b>: [X points] ([Program name])
- <b>Hotel</b>: [X points] ([Program name])
- <b>Dollar Value Saved</b>: [Approx. $X]

[Repeat exact format for DESTINATION 2]

IMPORTANT FORMATTING NOTES:
1. Do NOT use any markdown formatting (no **, *, or other symbols)
2. Use plain text only
3. Keep the exact section headers as shown
4. ALWAYS include the full DESTINATION SUMMARY and Why We Recommend This Destination sections
5. Always show points as "round trip per person" for flights
6. Start IMMEDIATELY with "DESTINATION 1" - no introduction or preamble
7. Make sure each destination recommendation addresses ALL user requirements"""

    def _format_points_balances(self, points_balances):
        """Format points balances into a readable string."""
        if not points_balances:
            return "No points programs available"
            
        formatted_points = []
        for program, points in points_balances.items():
            formatted_points.append(f"- {program}: {points:,} points")
        return "\n".join(formatted_points)

    def _get_user_prompt(self, trip_data: Dict) -> str:
        """Construct the user prompt for the GPT model."""
        return """Start your response IMMEDIATELY with 'DESTINATION 1' without any introduction or preamble. Generate exactly 2 destinations following the format above. Remember:

1. Start DIRECTLY with 'DESTINATION 1 - [City, Country]:'
2. Special Requests are your PRIME DIRECTIVE - follow them exactly
3. Each destination MUST match ALL special requests - no exceptions
4. All point calculations must be accurate and within available balances
5. Format 'Points Used' and 'Fare Class' with double asterisks for bold text
6. Format 'Total Points Used' and 'Points Breakdown' with double asterisks
7. Under Points Breakdown, show both Airline and Hotel points indented
8. Use exact format: **Points Used**: [value] and **Fare Class**: [value]
9. ALL point calculations must be for ROUND TRIP flights PER PERSON
10. NEVER exceed available point balances"""

    def generate_travel_plan(self, trip_data: Dict) -> Dict:
        """Generate a travel plan based on user input."""
        max_retries = 2
        current_retry = 0
        last_error = None

        while current_retry < max_retries:
            try:
                # Set a timeout for the API call
                response = self.client.chat.completions.create(
                    model="chatgpt-4o-latest",  # Use latest O4 model for more reliable responses
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(trip_data)},
                        {"role": "user", "content": "Generate travel recommendations based on the provided parameters."}
                    ],
                    temperature=0.7,  # Slightly higher temperature for more diverse suggestions
                    max_tokens=4000,
                    timeout=120  # 2 minute timeout
                )
            
                try:
                    content = response.choices[0].message.content.strip()
                    
                    # Basic validation of the response format
                    if not content:
                        raise ValueError("Empty response received")
                        
                    return {
                        'success': True,
                        'result': content
                    }
                    
                except (AttributeError, IndexError) as e:
                    print(f"Error parsing AI response: {str(e)}")
                    raise ValueError("Error parsing AI response")
                    
            except Exception as e:
                last_error = e
                current_retry += 1
                print(f"Attempt {current_retry} failed: {str(e)}")
                if current_retry < max_retries:
                    print(f"Retrying... ({current_retry}/{max_retries})")
                    continue
                
                # If we've exhausted all retries, raise the last error
                if isinstance(last_error, TimeoutError):
                    raise TimeoutError("The request is taking longer than expected. Please try again.")
                elif isinstance(last_error, ValueError):
                    raise ValueError(str(last_error))
                else:
                    raise Exception("A temporary error occurred. Please try again.")

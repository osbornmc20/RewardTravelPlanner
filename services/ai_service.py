from typing import Dict, List
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from flask_login import current_user
from models import PointsProgram
from flask import current_app

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")

client = OpenAI(api_key=api_key)

class TravelPlanGenerator:
    def __init__(self):
        pass
        
    def _get_system_prompt(self, trip_data: Dict) -> str:
        """Construct the system prompt for the GPT model."""
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
⚠️ SPECIAL REQUESTS (PRIME DIRECTIVE - MUST BE FOLLOWED) ⚠️
{special_requests}

These special requests are your HIGHEST PRIORITY. They override all other considerations except point balance limits.
- If a request specifies certain regions/countries/cities, ONLY suggest destinations that match
- If a request excludes certain types of places, NEVER suggest those places
- If you're unsure if a destination meets ALL special requests, DO NOT suggest it
- Treat these as strict requirements, not preferences

Example: If the request says "Only show European destinations":
✓ DO suggest: Paris, France
✓ DO suggest: Rome, Italy
✓ DO suggest: Barcelona, Spain
✗ DO NOT suggest: Tokyo, Japan
✗ DO NOT suggest: New York, USA
✗ DO NOT suggest: Sydney, Australia

Your response will be REJECTED if it includes destinations that don't match the special requests.
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

CRITICAL REQUIREMENTS:
1. Special Requests are your PRIME DIRECTIVE - they must be followed exactly
2. Each destination MUST match ALL special requests - no exceptions
3. All point calculations must be accurate and within available balances
4. Economy and luxury options must be different
5. Luxury options must include premium economy, business or first class flights
6. Fare Type must be clearly specified for all flights
7. If you're unsure if a destination meets ALL special requests, choose a different one
8. ALWAYS show exactly 3 destinations, numbered 1, 2, and 3
9. ALL point calculations must be for ROUND TRIP flights PER PERSON
10. NEVER exceed available point balances
11. Consider seasonal factors for each destination:
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
1. Your Requirements: 
   - [List how this matches each of the user's special requests]
   - [Address any specific preferences mentioned]

2. Seasonal Sweet Spot:
   - Weather: [Current season's weather patterns and why they're ideal]
   - Local Events: [Key festivals, events, or activities during these months]
   
3. Points Strategy:
   - Award Availability: [Current patterns for this route/destination]
   - Peak/Off-Peak: [How timing affects point redemptions]
   - Special Opportunities: [Any point transfer bonuses or sweet spot redemptions]

OPTION A - ECONOMY EXPERIENCE
Flight Details:
- Route: [Airport to destination]
- Airline: [Airline name]
- Points Program: [Program name]
- Points Used: [X points round trip per person]
- Fare Type: Economy
- Award Availability: [Typical availability for these months]

Hotel Option:
- Property: [Hotel name]
- Points Program: [Program name]
- Total Points Needed: [X points (X points per night)]
- Property Details: [Brief description]

Value Analysis:
- Points Used: [Total points used]
- Points Breakdown:
  * Airline: [X points] ([Program name])
  * Hotel: [X points] ([Program name])
- Dollar Value Saved: [Approx. $X]

OPTION B - LUXURY EXPERIENCE
Flight Details:
- Route: [Airport to destination]
- Airline: [Airline name]
- Points Program: [Program name]
- Points Used: [X points round trip per person]
- Fare Type: [Premium Economy/Business/First]
- Award Availability: [Typical availability for these months]

Hotel Option:
- Property: [Luxury hotel name]
- Points Program: [Program name]
- Total Points Needed: [X points (X points per night)]
- Property Details: [Brief luxury description]

Value Analysis:
- Points Used: [Total points used]
- Points Breakdown:
  * Airline: [X points] ([Program name])
  * Hotel: [X points] ([Program name])
- Dollar Value Saved: [Approx. $X]

[Repeat exact format for DESTINATION 2 and DESTINATION 3]

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
        return """Start your response IMMEDIATELY with 'DESTINATION 1' without any introduction or preamble. Generate exactly 3 destinations following the format above. Remember:

1. Start DIRECTLY with 'DESTINATION 1 - [City, Country]:'
2. Special Requests are your PRIME DIRECTIVE - follow them exactly
3. Each destination MUST match ALL special requests - no exceptions
4. All point calculations must be accurate and within available balances
5. Economy and luxury options must be different
6. Luxury options must include premium economy, business or first class flights
7. Fare Type must be clearly specified for all flights
8. If you're unsure if a destination meets ALL special requests, choose a different one
9. ALL point calculations must be for ROUND TRIP flights PER PERSON
10. NEVER exceed available point balances"""

    def generate_travel_plan(self, trip_data: Dict) -> Dict:
        """Generate a travel plan based on user input."""
        try:
            # Set a timeout for the API call
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",  # Use latest GPT-4 Turbo model
                messages=[
                    {"role": "system", "content": self._get_system_prompt(trip_data)},
                    {"role": "user", "content": "Generate travel recommendations based on the provided parameters."}
                ],
                temperature=0.7,  # Balanced temperature for creativity and consistency
                max_tokens=4096,  # Standard token limit
                timeout=60  # 60 second timeout
            )
            
            try:
                content = response.choices[0].message.content.strip()
                
                # Basic validation of the response format
                if not content:
                    raise ValueError("No travel plan was generated. Please try again - it usually works on the second try!")
                    
                return {
                    'success': True,
                    'result': content
                }
                
            except (AttributeError, IndexError) as e:
                print(f"Error parsing AI response: {str(e)}")
                raise ValueError("A temporary error occurred while processing the AI response. Please try again - it usually works on the second try!")
                
        except Exception as e:
            print(f"Error in generate_travel_plan: {str(e)}")
            if "timeout" in str(e).lower():
                raise TimeoutError("The AI took a bit too long to respond. Please try again - it usually works on the second try!")
            raise

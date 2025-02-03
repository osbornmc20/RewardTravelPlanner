from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import requests
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from models import db, User, PointsProgram, Airport
from services.ai_service import TravelPlanGenerator

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# Database configuration
if os.getenv('RENDER'):
    # Production database (PostgreSQL on Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '').replace('postgres://', 'postgresql://')
else:
    # Local database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///points_tracker.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
with app.app_context():
    db.create_all()
    # Check if we need to populate airports
    if Airport.query.count() == 0:
        try:
            from populate_airports import populate_airports
            populate_airports()
        except Exception as e:
            print(f"Error populating airports: {e}")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define anonymous user class
class Anonymous(AnonymousUserMixin):
    @property
    def id(self):
        """Return None for id to match UserMixin pattern."""
        return None

    def get_id(self):
        """Return None for get_id to match UserMixin pattern."""
        return None

login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
org_id = os.getenv('OPENAI_ORG_ID')

# Extract project ID from API key (format: sk-proj-xxxx_...)
project_id = api_key.split('_')[0] if api_key else None
if project_id:
    print(f"Project ID: {project_id}")

# Common headers for OpenAI API requests
openai_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "OpenAI-Organization": org_id,
    "X-Project-ID": project_id  # Add project ID header
}

# Validate OpenAI API key and org ID
if not api_key:
    print("Warning: OpenAI API key not found in .env file.")
elif api_key == 'your-openai-api-key-here':
    print("Warning: OpenAI API key is still set to the default placeholder value.")
else:
    print("OpenAI API key loaded successfully.")

if not org_id:
    print("Warning: OpenAI organization ID not found in .env file.")
else:
    print(f"Using OpenAI organization: {org_id}")

# Test OpenAI API connection
try:
    # Try to list models to verify authentication
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers=openai_headers
    )
    response.raise_for_status()
    print("Successfully connected to OpenAI API")
    print("Available models:", response.json())
except requests.exceptions.RequestException as e:
    print(f"Error testing OpenAI connection: {str(e)}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_data = e.response.json()
            print(f"Error details: {error_data}")
        except:
            pass

# Routes for authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Routes for points programs
@app.route('/points/add', methods=['POST'])
def add_points_program():
    data = request.json
    
    if current_user.is_authenticated:
        # Handle logged-in user
        program = PointsProgram(
            program_name=data['program_name'],
            points_balance=data['points_balance'],
            user_id=current_user.id
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id
    else:
        # Handle non-logged-in user with session storage
        if 'temp_programs' not in session:
            session['temp_programs'] = []
            session['temp_program_id'] = 0
        
        # Create a temporary program with a session-unique ID
        session['temp_program_id'] += 1
        program_id = f"temp_{session['temp_program_id']}"
        
        temp_program = {
            'id': program_id,
            'program_name': data['program_name'],
            'points_balance': data['points_balance']
        }
        
        session['temp_programs'].append(temp_program)
        session.modified = True
    
    return jsonify({'status': 'success', 'id': program_id})

@app.route('/points/update', methods=['POST'])
def update_points_program():
    data = request.json
    
    if current_user.is_authenticated:
        # Handle logged-in user
        program = PointsProgram.query.get(data['id'])
        if program and program.user_id == current_user.id:
            program.points_balance = data['points_balance']
            db.session.commit()
            return jsonify({'status': 'success'})
    else:
        # Handle non-logged-in user
        if 'temp_programs' in session:
            for program in session['temp_programs']:
                if str(program['id']) == str(data['id']):
                    program['points_balance'] = data['points_balance']
                    session.modified = True
                    return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Program not found'}), 404

@app.route('/points/delete', methods=['POST'])
def delete_points_program():
    data = request.json
    
    if current_user.is_authenticated:
        # Handle logged-in user
        program = PointsProgram.query.get(data['id'])
        if program and program.user_id == current_user.id:
            db.session.delete(program)
            db.session.commit()
            return jsonify({'status': 'success'})
    else:
        # Handle non-logged-in user
        if 'temp_programs' in session:
            session['temp_programs'] = [p for p in session['temp_programs'] if str(p['id']) != str(data['id'])]
            session.modified = True
            return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Program not found'}), 404

@app.route('/points/list')
def list_points_programs():
    if current_user.is_authenticated:
        # Handle logged-in user
        programs = PointsProgram.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'status': 'success',
            'programs': [{
                'id': p.id,
                'program_name': p.program_name,
                'points_balance': p.points_balance
            } for p in programs]
        })
    else:
        # Handle non-logged-in user
        return jsonify({
            'status': 'success',
            'programs': session.get('temp_programs', [])
        })

# Airport search endpoint
@app.route('/search_airports')
def search_airports():
    query = request.args.get('query', '').upper()
    if len(query) < 2:
        return jsonify([])
    
    # Search by IATA code, city, or airport name
    airports = Airport.query.filter(
        db.or_(
            Airport.code.like(f"{query}%"),
            Airport.city.ilike(f"%{query}%"),
            Airport.name.ilike(f"%{query}%")
        )
    ).limit(10).all()
    
    return jsonify([airport.to_dict() for airport in airports])

# Main route
@app.route('/')
def index():
    points_programs = []
    if current_user.is_authenticated:
        points_programs = PointsProgram.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', points_programs=points_programs)

# Trip planning route
@app.route('/api/trip/plan', methods=['POST'])
@login_required
def plan_trip():
    if not api_key:
        return jsonify({
            'status': 'error',
            'message': 'OpenAI API key not configured properly.'
        }), 500

    data = request.json
    prompt = generate_trip_prompt(data)
    
    try:
        # Call OpenAI API using requests library
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=openai_headers,
            json={
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert travel planner with access to real-time flight, weather, and event information. 
                        Your task is to create detailed, personalized trip plans based on user preferences.
                        Always format your response as valid JSON objects."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        # Print response headers and status for debugging
        print("Response Status:", response.status_code)
        print("Response Headers:", dict(response.headers))
        
        # Check for authentication errors
        if response.status_code == 401:
            error_data = response.json()
            print(f"Authentication Error: {error_data}")
            return jsonify({
                'status': 'error',
                'message': f'OpenAI API authentication failed: {error_data.get("error", {}).get("message", "Unknown error")}'
            }), 500
        
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        print("OpenAI API Response:", result)
        
        # Extract the trip plan from the response
        trip_plan = json.loads(result['choices'][0]['message']['content'])
        
        return jsonify({
            'status': 'success',
            'trip_plan': trip_plan
        })
        
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        print(f"Request Exception: {error_message}")
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', str(e))
                print(f"Error Response: {error_data}")
            except:
                pass
        
        return jsonify({
            'status': 'error',
            'message': f'Error generating trip plan: {error_message}'
        }), 500

def generate_trip_prompt(trip_data):
    trip_types = ' and '.join(trip_data['trip_types'])
    airports = ', '.join(trip_data['airports'])
    duration = trip_data['trip_length']
    max_flight_length = trip_data['max_flight_length']
    direct_flights = 'direct flights only' if trip_data['direct_flights'] else 'including connecting flights'
    preferences = trip_data.get('user_preferences', '')
    
    # Include points programs information in the prompt
    points_info = ""
    if trip_data.get('points_programs'):
        points_info = "\nI have the following loyalty program points available:\n"
        for program in trip_data['points_programs']:
            points_info += f"- {program['program_name']}: {program['points_balance']} points\n"
    
    return f"""Given the following trip preferences, generate exactly 3 destination options with points redemption options.
    Format the response as a valid JSON object with this exact structure:

    {{
        "destinations": [
            {{
                "name": "City, Country",
                "preference_match": "Brief explanation of why this destination matches preferences",
                "economy": {{
                    "route": "LAX to XYZ",
                    "airline": "Airline Name",
                    "points_program": "Program Name",
                    "points_used": "35,000 points",
                    "total_points": "70,000 points round trip",
                    "hotel": {{
                        "property": "Hotel Name and Location",
                        "points_program": "Program Name",
                        "total_points": "90,000 points (15,000 points per night)",
                        "details": "Brief description of property and location"
                    }},
                    "value_analysis": {{
                        "total_points": "160,000 points",
                        "airline_points": "70,000 points (Program Name)",
                        "hotel_points": "90,000 points (Program Name)",
                        "dollar_value": "Approx. $3,280 (using point valuations provided)"
                    }}
                }},
                "luxury": {{
                    "route": "LAX to XYZ",
                    "airline": "Airline Name",
                    "points_program": "Program Name",
                    "points_used": "35,000 points",
                    "total_points": "70,000 points round trip",
                    "hotel": {{
                        "property": "Luxury Hotel Name and Location",
                        "points_program": "Program Name",
                        "total_points": "150,000 points (25,000 points per night)",
                        "details": "Brief description of luxury amenities"
                    }},
                    "value_analysis": {{
                        "total_points": "220,000 points",
                        "airline_points": "70,000 points (Program Name)",
                        "hotel_points": "150,000 points (Program Name)",
                        "dollar_value": "Approx. $4,510 (using point valuations provided)"
                    }}
                }}
            }}
        ]
    }}

    Trip Preferences:
    - Trip Types: {trip_types}
    - Departing from: {airports}
    - Trip Length: {duration} days
    - Flight Preferences: {direct_flights}, max {max_flight_length} hours
    - Additional Preferences: {preferences}
    {points_info}

    Requirements:
    1. Provide EXACTLY 3 different destinations
    2. All points calculations should be realistic based on current redemption rates
    3. Each destination must include both economy and luxury options
    4. Keep property details and preference match explanations brief and focused
    5. Format all points values with commas and the word "points"
    6. Include "round trip" in total points for flights
    7. Include "points per night" in hotel total points
    8. Start all dollar values with "Approx. $"
    """

@app.route('/generate_trip', methods=['POST'])
def generate_trip():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Initialize the travel plan generator
        travel_planner = TravelPlanGenerator()
        
        # Generate the travel plan
        result = travel_planner.generate_travel_plan(data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in generate_trip route: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_openai', methods=['GET'])
def test_openai():
    try:
        from services.ai_service import client
        # Try to list models as a simple API test
        models = client.models.list()
        return jsonify({
            'success': True,
            'message': 'OpenAI API connection successful',
            'models': [model.id for model in models.data[:5]]  # Show first 5 models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_static')
def test_static():
    """Test endpoint to verify static files are being served correctly"""
    return jsonify({
        'js_path': url_for('static', filename='js/trip_planner.js'),
        'css_path': url_for('static', filename='css/trip_planner.css')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5030)

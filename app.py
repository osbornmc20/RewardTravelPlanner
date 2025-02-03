from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import requests
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from models import db, User, PointsProgram, Airport
from services.ai_service import TravelPlanGenerator
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# Database configuration with connection pooling
if os.getenv('RENDER'):
    # Production database (PostgreSQL on Render)
    db_url = os.getenv('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    engine = create_engine(
        db_url,
        poolclass=QueuePool,
        pool_size=5,  # Conservative pool size
        max_overflow=5,  # Limited overflow
        pool_timeout=30,
        pool_pre_ping=True,  # Verify connection before using
        pool_recycle=1800,  # Recycle connections every 30 minutes
        pool_use_lifo=True  # Last In First Out for better performance
    )
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 5,
        'pool_timeout': 30,
        'pool_pre_ping': True,
        'pool_recycle': 1800,
        'pool_use_lifo': True
    }
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Local database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///points_tracker.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

def init_db():
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.create_all()
                # Check if we need to populate airports
                if Airport.query.count() == 0:
                    try:
                        from populate_airports import populate_airports
                        populate_airports()
                    except Exception as e:
                        print(f"Error populating airports: {e}")
            return  # Success, exit the function
        except Exception as e:
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                print(f"Database initialization attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Final database initialization attempt failed: {e}")
                raise

# Initialize database with retry logic
init_db()

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
        
        try:
            # Generate the travel plan
            result = travel_planner.generate_travel_plan(data)
            return jsonify(result)
        except Exception as e:
            print(f"Error generating travel plan: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error generating travel plan. Please try again.'
            }), 500
        
    except Exception as e:
        print(f"Error in generate_trip route: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400  # Changed to 400 for client errors

# Test OpenAI API connection
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

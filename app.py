from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory, make_response
from utils.sitemap import SitemapGenerator
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from datetime import datetime
import os
from dotenv import load_dotenv
import json
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from models import db, User, PointsProgram
from services.ai_service import TravelPlanGenerator, TripValidationError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create tables
with app.app_context():
    # Only create tables if they don't exist
    db.create_all()

def init_db():
    """Initialize database tables. Should only be called once when setting up the app for the first time."""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempting database initialization (attempt {retry_count + 1})")
            with app.app_context():
                # Drop all tables and recreate them
                db.drop_all()
                db.create_all()
                
                print("Database initialization successful")
                return
                
        except Exception as e:
            print(f"Database initialization attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            if retry_count == max_retries:
                print(f"Final database initialization attempt failed: {e}")
                raise

# Initialize database with retry logic
# Only uncomment this when you need to reset the database
# init_db()

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
org_id = os.getenv('OPENAI_ORG_ID')

# Anonymous user class for Flask-Login
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.points_programs = []

login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes
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
    program_type = data.get('program_type')
    program_name = data.get('program_name')
    points_balance = data.get('points_balance')
    
    if not program_type or not program_name or points_balance is None:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if current_user.is_authenticated:
        # Add program to database for logged-in user
        program = PointsProgram(
            user_id=current_user.id,
            program_type=program_type,
            program_name=program_name,
            points_balance=points_balance
        )
        db.session.add(program)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'program': {
                'id': program.id,
                'program_type': program.program_type,
                'program_name': program.program_name,
                'points_balance': program.points_balance
            }
        })
    else:
        # Store program in session for non-logged-in user
        temp_programs = session.get('temp_programs', [])
        program_id = len(temp_programs) + 1
        program_data = {
            'id': program_id,
            'program_type': program_type,
            'program_name': program_name,
            'points_balance': points_balance
        }
        temp_programs.append(program_data)
        session['temp_programs'] = temp_programs
        
        return jsonify({
            'success': True,
            'program': program_data
        })

@app.route('/points/update', methods=['POST'])
def update_points_program():
    data = request.json
    program_id = data.get('id')
    points_balance = data.get('points_balance')
    
    if program_id is None or points_balance is None:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    if current_user.is_authenticated:
        # Update program in database for logged-in user
        program = PointsProgram.query.filter_by(id=program_id, user_id=current_user.id).first()
        if not program:
            return jsonify({'status': 'error', 'message': 'Program not found'}), 404
        
        program.points_balance = points_balance
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'program': {
                'id': program.id,
                'program_name': program.program_name,
                'points_balance': program.points_balance
            }
        })
    else:
        # Update program in session for non-logged-in user
        temp_programs = session.get('temp_programs', [])
        program = next((p for p in temp_programs if p['id'] == program_id), None)
        if not program:
            return jsonify({'status': 'error', 'message': 'Program not found'}), 404
        
        program['points_balance'] = points_balance
        session['temp_programs'] = temp_programs
        
        return jsonify({
            'status': 'success',
            'program': program
        })

@app.route('/points/delete', methods=['POST'])
def delete_points_program():
    data = request.json
    program_id = data.get('id')
    
    if program_id is None:
        return jsonify({'success': False, 'error': 'Missing program ID'}), 400
    
    if current_user.is_authenticated:
        # Delete program from database for logged-in user
        program = PointsProgram.query.filter_by(id=program_id, user_id=current_user.id).first()
        if not program:
            return jsonify({'success': False, 'error': 'Program not found'}), 404
        
        db.session.delete(program)
        db.session.commit()
        
        return jsonify({'success': True})
    else:
        # Delete program from session for non-logged-in user
        temp_programs = session.get('temp_programs', [])
        temp_programs = [p for p in temp_programs if p['id'] != program_id]
        session['temp_programs'] = temp_programs
        session.modified = True  # Ensure session is saved
        
        return jsonify({'success': True})

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

# Main route
@app.route('/')
def index():
    points_programs = []
    if current_user.is_authenticated:
        points_programs = PointsProgram.query.filter_by(user_id=current_user.id).all()
    else:
        # Get temporary programs from session for non-logged-in users
        points_programs = [type('PointsProgram', (), p) for p in session.get('temp_programs', [])]
    
    # Get today's date for date inputs
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('index.html', points_programs=points_programs, today=today)

# Trip planning route
@app.route('/generate_trip', methods=['POST'])
def generate_trip():
    """Generate trip ideas based on user input."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Request must be JSON'
        }), 400
        
    try:
        # Store the request data so it can be accessed multiple times if needed
        data = request.get_json()
        request.data_cache = data  # Cache the data in case it's needed elsewhere
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Initialize the travel plan generator with a timeout
        travel_planner = TravelPlanGenerator()
        
        try:
            # Generate the travel plan with a timeout
            result = travel_planner.generate_travel_plan(data)
            
            # Validate the result
            if not isinstance(result, dict):
                return jsonify({
                    'success': False,
                    'error': 'Invalid response format from AI service'
                }), 500
                
            return jsonify(result)
            
        except TripValidationError as e:
            print(f"Trip validation error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
            
        except RateLimitError:
            return jsonify({
                'success': False,
                'error': 'The service is briefly busy. Please try again in a few moments - it usually works on the second try!'
            }), 429
        except APIConnectionError:
            return jsonify({
                'success': False,
                'error': 'Connection to the AI service failed. Please try again in a few moments.'
            }), 502
        except APIError:
            return jsonify({
                'success': False,
                'error': 'The service is temporarily unavailable. Please try again - it usually works on the second try!'
            }), 503
        except APIConnectionError:
            return jsonify({
                'success': False,
                'error': 'Having trouble connecting to the service. Please try again - it usually works on the second try!'
            }), 503
        except TimeoutError:
            return jsonify({
                'success': False,
                'error': 'The request took a bit too long. Please try again - it usually works on the second try!'
            }), 504
        except Exception as e:
            print(f"Error generating travel plan: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'A temporary error occurred. Please try again - it usually works on the second try!'
            }), 500
        
    except Exception as e:
        print(f"Error parsing request data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid request data format'
        }), 400

# Test OpenAI API connection
@app.route('/test_openai', methods=['GET'])
def test_openai():
    try:
        # Get OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        client = OpenAI(api_key=api_key)
        
        # Try a simple chat completion as a test
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        return jsonify({
            'success': True,
            'message': 'OpenAI API connection successful',
            'response': response.choices[0].message.content
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

# Recommendations routes
@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    sitemap = SitemapGenerator('https://goaskmarshall.com')
    
    # Add main pages
    sitemap.add_url('/', priority=1.0, changefreq='daily')
    sitemap.add_url('/recommendations', priority=0.9, changefreq='weekly')
    
    # Add guide pages with their slugs
    guides = [
        {'slug': 'best-mexican-beach-towns', 'title': 'Best lesser-known Mexican beach towns'},
        {'slug': 'budapest-food-guide', 'title': 'Budapest Food & Activities Guide'},
        {'slug': 'amsterdam-food-guide', 'title': 'Where to Eat in Amsterdam'},
        {'slug': 'southwest-road-trip', 'title': 'Great American Southwest Road Trip'}
    ]
    
    for guide in guides:
        sitemap.add_url(f'/guides/{guide["slug"]}', priority=0.8, changefreq='monthly')
    
    response = make_response(sitemap.generate())
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/api/recommendations')
def get_recommendations():
    recommendations = [
        {
            "title": "Best lesser-known Mexican beach towns",
            "location": "Mexico",
            "author": "Go Ask Marshall",
            "image": url_for('static', filename='images/recommendations/mexico-beaches.jpg'),
            "url": "https://mindtrip.ai/z/AHHZKE",
            "places": "7 places"
        },
        {
            "title": "Guide to Budapest - Food & Activities",
            "location": "Budapest, Hungary",
            "author": "Go Ask Marshall",
            "image": url_for('static', filename='images/recommendations/budapest-guide.jpg'),
            "url": "https://mindtrip.ai/z/Scbzkj",
            "places": "21 places"
        },
        {
            "title": "Where to Eat in Amsterdam if you don't like Dutch food",
            "location": "Amsterdam, The Netherlands",
            "author": "Go Ask Marshall",
            "image": url_for('static', filename='images/recommendations/amsterdam-food.jpg'),
            "url": "https://mindtrip.ai/z/wGjnrt",
            "places": "11 places"
        },
        {
            "title": "The Great American Southwest - A Road Trip",
            "location": "United States",
            "author": "Go Ask Marshall",
            "image": url_for('static', filename='images/recommendations/southwest-roadtrip.jpg'),
            "url": "https://mindtrip.ai/z/BWizlt",
            "places": "10 days"
        }
    ]
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5037)

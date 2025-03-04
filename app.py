from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory, make_response
from utils.sitemap import SitemapGenerator
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from services.ai_service import TravelPlanGenerator, TripValidationError

# Create Flask app
app = Flask(__name__)

# Enhanced security settings
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after app is created
from models import db, User, PointsProgram
from models.review import Review

# Initialize the database with the app
db.init_app(app)

# Load environment variables
load_dotenv()

# Session security settings
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cross-site requests
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session expiration

# Initialize extensions
# db.init_app(app) is already called above

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Session validation middleware
@app.before_request
def validate_session():
    # Skip for static files and authentication routes
    if request.path.startswith('/static') or request.path in ['/login', '/logout', '/register']:
        return
        
    # Check if user is authenticated but session is missing user_id
    if current_user.is_authenticated and 'user_id' not in session:
        print(f"Session integrity issue detected: Missing user_id for {current_user.email if hasattr(current_user, 'email') else 'unknown user'}")
        logout_user()
        session.clear()
        flash('Your session has expired. Please login again.')
        return redirect(url_for('login'))
        
    # Check if session user_id doesn't match current user
    if current_user.is_authenticated and 'user_id' in session and session['user_id'] != current_user.id:
        print(f"Session integrity issue detected: User ID mismatch for {current_user.email}")
        logout_user()
        session.clear()
        flash('Your session has expired. Please login again.')
        return redirect(url_for('login'))

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
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required')
            return render_template('forgot_password.html')
            
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            db.session.commit()
            
            # Create reset link
            reset_url = url_for('reset_password', token=token, email=email, _external=True)
            
            # Display the reset link directly on the page
            return render_template('reset_link.html', reset_url=reset_url, email=email)
        else:
            # For a demo app without sensitive data, we can be more user-friendly
            flash('No account found with that email address. Please check the email or register a new account.')
            return render_template('forgot_password.html')
        
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    email = request.args.get('email')
    if not email or not token:
        return render_template('error.html', 
                              error_title="Invalid Reset Link",
                              error_message="The password reset link is missing required information.",
                              back_link=url_for('forgot_password'),
                              back_text="Try Again")
        
    user = User.query.filter_by(email=email).first()
    if not user or not user.reset_token:
        return render_template('error.html', 
                              error_title="Invalid Reset Link",
                              error_message="This reset link is invalid or has already been used.",
                              back_link=url_for('forgot_password'),
                              back_text="Request a New Link")
        
    # For GET requests, verify token and show form
    if request.method == 'GET':
        if user.verify_reset_token(token):
            return render_template('reset_password.html', token=token, email=email)
        else:
            return render_template('error.html', 
                                  error_title="Expired Reset Link",
                                  error_message="This password reset link has expired. Reset links are valid for 24 hours.",
                                  back_link=url_for('forgot_password'),
                                  back_text="Request a New Link")
    
    # For POST requests, process the form submission
    if request.method == 'POST':
        if not user.verify_reset_token(token):
            return render_template('error.html', 
                                  error_title="Expired Reset Link",
                                  error_message="This password reset link has expired. Reset links are valid for 24 hours.",
                                  back_link=url_for('forgot_password'),
                                  back_text="Request a New Link")
            
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        errors = []
        if not password:
            errors.append('New password is required')
        if not confirm_password:
            errors.append('Password confirmation is required')
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match')
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long')
            
        if errors:
            for error in errors:
                flash(error)
            return render_template('reset_password.html', token=token, email=email)
        
        # Update password and clear token
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        
        # Return success page instead of redirecting with a flash message
        return render_template('password_reset_success.html', login_url=url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear any existing session
    session.clear()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not email or not password:
            flash('Email and password are required')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Set session as permanent and login user
        session.permanent = True
        login_user(user, remember=True)
        
        # Add session identifier
        session['user_id'] = user.id
        session['login_time'] = datetime.now().isoformat()
        
        # Log the registration
        print(f"New user registered: {user.email} at {session['login_time']}")
        
        flash('Registration successful! Welcome to Reward Travel Planner.')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any existing session
    session.clear()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not email or not password:
            flash('Email and password are required')
            return render_template('login.html')
            
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Set session as permanent and login user
            session.permanent = True
            login_user(user, remember=True)
            
            # Add a session identifier
            session['user_id'] = user.id
            session['login_time'] = datetime.now().isoformat()
            
            # Log the login
            print(f"User logged in: {user.email} at {session['login_time']}")
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Log the logout
    if current_user.is_authenticated:
        print(f"User logged out: {current_user.email}")
    
    # Clear the session
    session.clear()
    
    # Logout the user
    logout_user()
    
    flash('You have been logged out successfully')
    return redirect(url_for('login'))

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
            model="gpt-4o-mini",
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

# Travel Guides routes
@app.route('/travel-guides')
def travel_guides():
    return render_template('travel-guides.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/.well-known/security.txt')
def security_txt():
    return send_from_directory(os.path.join('static', '.well-known'), 'security.txt')

@app.route('/sitemap.xml')
def sitemap():
    sitemap = SitemapGenerator('https://goaskmarshall.com')
    
    # Add main pages
    sitemap.add_url('/', priority=1.0, changefreq='daily')
    sitemap.add_url('/travel-guides', priority=0.9, changefreq='weekly')
    sitemap.add_url('/hotel-rankings', priority=0.9, changefreq='monthly')
    
    # Add guide pages with their slugs
    guides = [
        {'slug': 'best-mexican-beach-towns', 'title': 'Best lesser-known Mexican beach towns'},
        {'slug': 'budapest-food-guide', 'title': 'Budapest Food & Activities Guide'},
        {'slug': 'amsterdam-food-guide', 'title': 'Where to Eat in Amsterdam'},
        {'slug': 'southwest-road-trip', 'title': 'Great American Southwest Road Trip'}
    ]
    
    for guide in guides:
        sitemap.add_url(f'/guides/{guide["slug"]}', priority=0.8, changefreq='monthly')
    
    # Add blog review pages
    with app.app_context():
        try:
            reviews = Review.get_all_published()
            for review in reviews:
                sitemap.add_url(f'/reviews/{review.slug}', priority=0.8, changefreq='weekly')
        except Exception as e:
            app.logger.error(f"Error adding reviews to sitemap: {str(e)}")
    
    response = make_response(sitemap.generate())
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/api/travel-guides')
def get_travel_guides():
    guides = [
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
    return jsonify(guides)

@app.route('/hotel-rankings')
def hotel_rankings():
    return render_template('hotel-rankings.html')

@app.route('/api/hotel-rankings')
def get_hotel_rankings():
    import csv
    import os
    
    hotels = []
    csv_file = os.path.join(app.root_path, 'data', 'Hotel Reviews.csv')
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            hotels.append({
                'name': row['Hotel Name'],
                'city': row['City'],
                'country': row['Country'],
                'category': row['Category'],
                'priceRange': row['Price Range'],
                'airportDistance': row['Distance from\nAirport'],
                'hasStayed': row['Have I \nStayed? (Y/N)'].strip().upper() == 'Y',
                'rating': float(row['My Rating']),
                'notes': row['Notes'],
                'website': ''  # We'll need to add this to the CSV
            })
    
    return jsonify(hotels)

# Review routes
@app.route('/reviews/<slug>')
def view_review(slug):
    review = Review.get_by_slug(slug)
    if not review:
        return render_template('error.html', 
                              error_title="Review Not Found",
                              error_message="The review you're looking for doesn't exist or has been removed.",
                              back_link=url_for('travel_guides'),
                              back_text="Back to Travel Guides")
    
    return render_template('review.html', review=review)

@app.route('/api/reviews')
def get_reviews():
    reviews = Review.get_all_published()
    result = []
    for review in reviews:
        result.append({
            "title": review.title,
            "slug": review.slug,
            "location": review.location,
            "summary": review.summary,
            "author": review.author,
            "image": review.image,
            "created_at": review.created_at.strftime('%Y-%m-%d'),
            "url": url_for('view_review', slug=review.slug)
        })
    return jsonify({"reviews": result})

@app.route('/admin/reviews', methods=['GET'])
@login_required
def admin_reviews():
    # Only allow admin users
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return redirect(url_for('index'))
        
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reviews/new', methods=['GET', 'POST'])
@login_required
def new_review():
    # Only allow admin users
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        summary = request.form.get('summary')
        content = request.form.get('content')
        image = request.form.get('image')
        is_published = 'is_published' in request.form
        
        review = Review(
            title=title,
            location=location,
            summary=summary,
            content=content,
            image=image
        )
        review.is_published = is_published
        
        db.session.add(review)
        db.session.commit()
        
        return redirect(url_for('admin_reviews'))
        
    return render_template('admin/review_form.html')

@app.route('/admin/reviews/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    # Only allow admin users
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return redirect(url_for('index'))
        
    review = Review.get_by_id(id)
    if not review:
        flash('Review not found', 'danger')
        return redirect(url_for('admin_reviews'))
    
    if request.method == 'POST':
        review.title = request.form.get('title')
        review.location = request.form.get('location')
        review.summary = request.form.get('summary')
        review.content = request.form.get('content')
        review.image = request.form.get('image')
        review.is_published = 'is_published' in request.form
        review.slug = slugify(review.title)
        
        db.session.commit()
        
        return redirect(url_for('admin_reviews'))
        
    return render_template('admin/review_form.html', review=review)

# Client-side error logging
@app.route('/api/log-error', methods=['POST'])
def log_client_error():
    try:
        error_data = request.json
        app.logger.error(f"Client error: {error_data}")
        return jsonify({"status": "success"})
    except Exception as e:
        app.logger.error(f"Error logging client error: {str(e)}")
        return jsonify({"status": "error"}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5041)

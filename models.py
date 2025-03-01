from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    points_programs = db.relationship('PointsProgram', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def generate_reset_token(self):
        """Generate a secure token for password reset"""
        import secrets
        from datetime import datetime, timedelta
        
        # Generate a secure token
        self.reset_token = secrets.token_urlsafe(32)
        # Set expiry to 24 hours from now
        self.reset_token_expiry = datetime.now() + timedelta(hours=24)
        return self.reset_token
        
    def verify_reset_token(self, token):
        """Verify if the reset token is valid"""
        from datetime import datetime
        
        if self.reset_token != token:
            return False
            
        if self.reset_token_expiry < datetime.now():
            # Token expired
            self.reset_token = None
            self.reset_token_expiry = None
            return False
            
        return True
        
    def clear_reset_token(self):
        """Clear the reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None

class PointsProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_type = db.Column(db.String(50), nullable=False)  # airline, hotel, or creditcard
    program_name = db.Column(db.String(100), nullable=False)
    points_balance = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

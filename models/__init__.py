# This file makes the models directory a Python package
from flask_sqlalchemy import SQLAlchemy

# Create a new SQLAlchemy instance
db = SQLAlchemy()

# Import models after db is defined
from models.user import User
from models.points_program import PointsProgram
from models.review import Review

def init_app(app):
    """Initialize the SQLAlchemy app"""
    db.init_app(app)

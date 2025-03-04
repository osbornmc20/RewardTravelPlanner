from datetime import datetime
from sqlalchemy.sql import func
from app import db
from slugify import slugify

class Guide(db.Model):
    __tablename__ = 'guides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_published = db.Column(db.Boolean, default=True)
    
    def __init__(self, title, location, url, image=None):
        self.title = title
        self.location = location
        self.url = url
        self.image = image
        self.slug = slugify(title)  # Automatically generate slug from title
    
    @staticmethod
    def get_all_published():
        """Get all published guides"""
        return Guide.query.filter_by(is_published=True).order_by(Guide.created_at.desc()).all()
    
    @staticmethod
    def get_by_slug(slug):
        """Get a guide by its slug"""
        return Guide.query.filter_by(slug=slug, is_published=True).first()

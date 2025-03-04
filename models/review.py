from datetime import datetime
from sqlalchemy.sql import func
from models import db
from slugify import slugify
import markdown
import bleach

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500))
    author = db.Column(db.String(100), default="Go Ask Marshall")
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_published = db.Column(db.Boolean, default=True)
    
    def __init__(self, title, location, summary, content, image=None, author="Go Ask Marshall"):
        self.title = title
        self.location = location
        self.summary = summary
        self.content = content
        self.image = image
        self.author = author
        self.slug = slugify(title)
    
    @property
    def html_content(self):
        """Convert markdown content to HTML with sanitization"""
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 
            'p', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'br', 'hr',
            'div', 'span', 'pre'
        ]
        allowed_attrs = {
            '*': ['class', 'id'],
            'a': ['href', 'rel', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        html = markdown.markdown(self.content, extensions=['extra'])
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    
    @staticmethod
    def get_all_published():
        """Get all published reviews"""
        return Review.query.filter_by(is_published=True).order_by(Review.created_at.desc()).all()
    
    @staticmethod
    def get_by_slug(slug):
        """Get a review by its slug"""
        if not slug:
            return None
        return Review.query.filter_by(slug=slug, is_published=True).first()
    
    @staticmethod
    def get_by_id(id):
        """Get a review by its ID with error handling"""
        try:
            return Review.query.get(id)
        except Exception as e:
            # Log the error but don't crash
            print(f"Error retrieving review with ID {id}: {str(e)}")
            return None

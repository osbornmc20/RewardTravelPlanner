from datetime import datetime
from sqlalchemy.sql import func
from models import db

class PointsProgram(db.Model):
    __tablename__ = 'points_programs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    program_name = db.Column(db.String(100), nullable=False)
    points_balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, user_id, program_name, points_balance=0):
        self.user_id = user_id
        self.program_name = program_name
        self.points_balance = points_balance
    
    def to_dict(self):
        return {
            'id': self.id,
            'program_name': self.program_name,
            'points_balance': self.points_balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

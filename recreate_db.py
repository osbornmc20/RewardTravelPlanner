from app import app, db
from models import User, PointsProgram

def recreate_database():
    """
    Recreate the database with the current schema.
    WARNING: This will delete all existing data.
    """
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables with the new schema
        db.create_all()
        print("Created all tables with the new schema")
        
        # Create a test user
        test_user = User(email="test@example.com")
        test_user.set_password("password123")
        db.session.add(test_user)
        
        # Add some sample points programs
        programs = [
            PointsProgram(program_type="airline", program_name="American Airlines AAdvantage", points_balance=50000, user_id=1),
            PointsProgram(program_type="hotel", program_name="Marriott Bonvoy", points_balance=75000, user_id=1),
            PointsProgram(program_type="creditcard", program_name="Chase Ultimate Rewards", points_balance=100000, user_id=1)
        ]
        
        db.session.add_all(programs)
        db.session.commit()
        
        print(f"Created test user: test@example.com with password: password123")
        print("Added sample points programs")
        
        return True

if __name__ == "__main__":
    recreate_database()

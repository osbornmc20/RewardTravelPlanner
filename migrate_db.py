import sqlite3
import os

def migrate_database():
    """Add reset_token and reset_token_expiry columns to the user table if they don't exist."""
    db_path = 'travel_planner.db'
    
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return False
    
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if reset_token column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add reset_token column if it doesn't exist
        if 'reset_token' not in column_names:
            print("Adding reset_token column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token TEXT UNIQUE")
        
        # Add reset_token_expiry column if it doesn't exist
        if 'reset_token_expiry' not in column_names:
            print("Adding reset_token_expiry column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN reset_token_expiry TIMESTAMP")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully.")
        return True
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()

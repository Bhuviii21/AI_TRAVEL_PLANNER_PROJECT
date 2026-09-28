import sqlite3
import os

def reset_database():
    # Delete existing database
    if os.path.exists("travel.db"):
        os.remove("travel.db")
        print("✅ Old database deleted")
    else:
        print("⏩ No database found")
    
    # Now run your app - it will create a fresh database with correct schema
    print("✅ Run your app now to create a fresh database")
    print("   Type: python app.py")

if __name__ == "__main__":
    reset_database()
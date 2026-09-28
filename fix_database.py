import sqlite3
import os

def fix_database():
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    
    print("🔧 Fixing database...")
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(trips)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Fix 1: Add user_id column if missing
    if 'user_id' not in columns:
        try:
            cursor.execute("ALTER TABLE trips ADD COLUMN user_id INTEGER")
            print("✅ Added user_id column")
        except Exception as e:
            print(f"Error adding user_id: {e}")
    
    # Fix 2: Add created_at column (without default)
    if 'created_at' not in columns:
        try:
            # SQLite can't add column with default value, so add without default
            cursor.execute("ALTER TABLE trips ADD COLUMN created_at TIMESTAMP")
            print("✅ Added created_at column (without default)")
            
            # Update existing rows with current timestamp
            cursor.execute("UPDATE trips SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            print("✅ Updated existing rows with current timestamp")
        except Exception as e:
            print(f"Error adding created_at: {e}")
    
    # Fix 3: Add latitude column if missing
    if 'latitude' not in columns:
        try:
            cursor.execute("ALTER TABLE trips ADD COLUMN latitude REAL")
            print("✅ Added latitude column")
        except Exception as e:
            print(f"Error adding latitude: {e}")
    
    # Fix 4: Add longitude column if missing
    if 'longitude' not in columns:
        try:
            cursor.execute("ALTER TABLE trips ADD COLUMN longitude REAL")
            print("✅ Added longitude column")
        except Exception as e:
            print(f"Error adding longitude: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database fix completed!")
    
    # Verify the changes
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(trips)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nUpdated columns: {columns}")
    conn.close()

if __name__ == "__main__":
    fix_database()
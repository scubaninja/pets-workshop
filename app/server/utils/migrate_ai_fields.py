"""
Migration script to add AI listing fields to existing dogs table.

Run this script if you have an existing database and want to add
the new AI-generated listing fields without losing data.

Usage:
    python utils/migrate_ai_fields.py
"""

import os
import sys
import sqlite3

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate():
    """Add AI listing columns to dogs table if they don't exist."""
    server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.environ.get('DATABASE_PATH', os.path.join(server_dir, 'dogshelter.db'))
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. No migration needed - tables will be created fresh.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(dogs)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # New columns to add
    new_columns = [
        ("ai_generated", "BOOLEAN DEFAULT 0"),
        ("image_path", "VARCHAR(500)"),
        ("seo_title", "VARCHAR(200)"),
        ("seo_keywords", "JSON"),
        ("tags", "JSON"),
        ("traits", "JSON"),
        ("adoption_highlights", "JSON"),
        ("categories", "JSON"),
        ("size_estimate", "VARCHAR(20)"),
        ("age_confidence", "VARCHAR(20)"),
    ]
    
    added = []
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE dogs ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not add column {col_name}: {e}")
    
    conn.commit()
    conn.close()
    
    if added:
        print(f"Successfully added columns: {', '.join(added)}")
    else:
        print("All AI listing columns already exist. No migration needed.")

if __name__ == '__main__':
    migrate()

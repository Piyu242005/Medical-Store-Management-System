import sys
import traceback

def main():
    try:
        # Import app and run its create_tables() which creates DB/admin and starts the server
        import app
        print('Imported app module successfully')
        # Remove existing SQLite DB file to avoid schema mismatch during development
        import os
        db_path = os.path.join(os.getcwd(), 'medical_store.db')
        if os.path.exists(db_path):
            print(f"Removing existing database at {db_path} to recreate schema...")
            try:
                os.remove(db_path)
            except Exception as e:
                print(f"Failed to remove existing DB file: {e}")
        app.create_tables()
    except Exception:
        print('Error while running create_tables():', file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

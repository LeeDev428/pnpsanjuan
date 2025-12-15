"""
Railway Database Initialization Script
Run this to set up your database tables
"""
import mysql.connector
import os
from config import DB_CONFIG

def init_railway_db():
    """Initialize database with all required tables"""
    try:
        print("Connecting to Railway MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)  # Use buffered cursor to avoid unread results
        
        print("Creating database tables...")
        
        # Read and execute database.sql
        with open('database.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read()
            # Split by semicolon and execute each command
            for command in sql_commands.split(';'):
                command = command.strip()
                if command and not command.startswith('--') and not command.startswith('CREATE DATABASE'):
                    try:
                        cursor.execute(command)
                        cursor.fetchall()  # Consume any results
                    except Exception as e:
                        print(f"Command failed (might be okay): {str(e)[:100]}")
        
        conn.commit()
        
        print("Running migration_add_status.sql...")
        try:
            with open('migration_add_status.sql', 'r', encoding='utf-8') as f:
                for command in f.read().split(';'):
                    command = command.strip()
                    if command and not command.startswith('--'):
                        try:
                            cursor.execute(command)
                            try:
                                cursor.fetchall()  # Consume any results
                            except:
                                pass
                        except Exception as e:
                            print(f"Migration command failed: {str(e)[:100]}")
            conn.commit()
        except FileNotFoundError:
            print("migration_add_status.sql not found, skipping...")
        
        print("Running migration_2fa.sql...")
        try:
            with open('migration_2fa.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
                # Execute the entire migration as one block
                for result in cursor.execute(sql_content, multi=True):
                    try:
                        result.fetchall()
                    except:
                        pass
            conn.commit()
        except FileNotFoundError:
            print("migration_2fa.sql not found, skipping...")
        except Exception as e:
            print(f"2FA migration note: {str(e)[:100]}")
        
        print("Running add_notifications.sql...")
        try:
            with open('add_notifications.sql', 'r', encoding='utf-8') as f:
                for command in f.read().split(';'):
                    command = command.strip()
                    if command and not command.startswith('--'):
                        try:
                            cursor.execute(command)
                            try:
                                cursor.fetchall()
                            except:
                                pass
                        except Exception as e:
                            print(f"Notifications migration note: {str(e)[:100]}")
            conn.commit()
        except FileNotFoundError:
            print("add_notifications.sql not found, skipping...")
        
        # Verify tables were created
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n✅ Database initialized successfully!")
        print(f"Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Railway Database Initialization")
    print("=" * 50)
    init_railway_db()

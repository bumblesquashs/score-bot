import sqlite3
import sys

DB_PATH = "database.sqlite3"

def migrate_up(conn: sqlite3.Connection):
    print("Migrating up...")
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT NOT NULL UNIQUE PRIMARY KEY
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            points_giver VARCHAR(64) NOT NULL,
            points_receiver VARCHAR(64) NOT NULL,
            message_text TEXT NOT NULL,
            points INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      
          FOREIGN KEY (points_receiver) REFERENCES users(discord_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        );
    """)
    conn.commit()

def migrate_down(conn: sqlite3.Connection):
    print("Migrating down...")
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS messages;
        DROP TABLE IF EXISTS users;
    """)
    conn.commit()



def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_db.py [up|down]")
        sys.exit(1)

    direction = sys.argv[1].lower()

    conn = sqlite3.connect(DB_PATH)

    if direction == "up":
        migrate_up(conn)
    elif direction == "down":
        migrate_down(conn)
    else:
        print("Unknown command. Use 'up' or 'down'.")
        sys.exit(1)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()

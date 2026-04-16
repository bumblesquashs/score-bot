import sqlite3
from .db_arguments import RecordMessageData
from .db_returns import ScoreboardRow

DB_PATH = "database.sqlite3"

conn = sqlite3.connect(DB_PATH)

def get_scoreboard_count() -> int:    
  cur = conn.cursor()
  cur.execute("SELECT COUNT(*) FROM users")
  
  return cur.fetchone()[0]


def get_score(user_discord_id: str) -> int | None:
  '''
  Find the current score for user with discord_id

  Returns an integer score, or None if there is no score for this user
  '''
  cur = conn.cursor()
  
  cur.execute("""
      SELECT SUM(score) FROM messages
      WHERE user_id = ?
  """, (user_discord_id,))

  result = cur.fetchone()
  conn.commit()
  cur.close()

  return result[0]


def record_message(data: RecordMessageData) -> None:
  '''
  Records a message that has been assigned points.

  Throws if there is an error
  '''
  cur = conn.cursor()

  ensure_user_exists(cur, data.points_receiver)

  # Insert message with points
  cur.execute("""
      INSERT INTO messages (points_receiver, points_giver, message_text, points)
      VALUES (?, ?, ?, ?)
  """, (data.points_receiver, data.points_giver, data.message_text, data.points))

  conn.commit()
  cur.close()

  

def get_scoreboard(page: int) -> list[ScoreboardRow]:
  '''
  Returns a scoreboard of the 15 top users with the highest score
  '''
  PAGE_SIZE = 15
  cur = conn.cursor()

  try:
      cur.execute(f"""
          SELECT 
              points_receiver AS discord_id,
              COALESCE(SUM(points), 0) AS total_score
          FROM messages
          GROUP BY points_receiver
          ORDER BY total_score DESC
          LIMIT 15 OFFSET {PAGE_SIZE * (page - 1)};
      """)

      rows = cur.fetchall()
      conn.commit()

      # Convert to ScoreboardRow objects
      return [
          ScoreboardRow(user_discord_id=row[0], total_score=row[1])
          for row in rows
      ]
  
  finally:
      cur.close()
  

def ensure_user_exists(cur: sqlite3.Cursor, discord_id: str) -> None:
  '''
  Creates a user if one does not already exist
  '''
  cur.execute("""
      INSERT OR IGNORE INTO users (discord_id)
      VALUES (?)
  """, (discord_id,))



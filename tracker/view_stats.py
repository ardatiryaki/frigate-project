import sqlite3
from datetime import datetime

DB_FILE = "tracker.db"

def get_daily_summary():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get logs for today
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT state, COUNT(*) FROM activity_logs WHERE timestamp LIKE ? GROUP BY state", (f"{today}%",))
    rows = cursor.fetchall()
    conn.close()
    
    print(f"--- Activity Report for {today} ---")
    total_seconds = 0
    stats = {}
    
    for state, count in rows:
        seconds = count * 5  # Each log is 5 seconds interval
        stats[state] = seconds
        total_seconds += seconds
        
    for state, seconds in stats.items():
        # Format seconds to H:M:S
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print(f"{state.ljust(10)}: {h}h {m}m {s}s")
        
    print("-----------------------------------")

if __name__ == "__main__":
    get_daily_summary()
    
    print("\nLast 5 Raw Entries:")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    conn.close()

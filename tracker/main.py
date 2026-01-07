import requests
import time
import json
import sqlite3
from datetime import datetime
import os

# Configuration
FRIGATE_URL = "http://localhost:5001"
CAMERA_NAME = "tapo_c222"
POLL_INTERVAL = 5  # seconds
DB_FILE = "tracker.db"

# Hardcoded zones from config for robustness (normalized 0-1)
ZONES = {
    'desk': [0.684,0.714,0.894,0.865,0.918,1,0.58,1,0.594,0.846],
    'bed': [0.283,0.654,0.501,0.681,0.415,1,0.03,1,0.135,0.822]
}

def init_db():
    """Initialize SQLite database and table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            state TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} initialized.")

def log_state(state):
    """Log the current state to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Use local time explicity instead of UTC default
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO activity_logs (timestamp, state) VALUES (?, ?)', (local_time, state))
    conn.commit()
    conn.close()

def is_point_in_polygon(x, y, poly_coords):
    """
    Ray casting algorithm to check if point (x,y) is inside polygon.
    poly_coords: [x1, y1, x2, y2, ...]
    """
    # Convert flat list to (x,y) tuples
    polygon = list(zip(poly_coords[0::2], poly_coords[1::2]))
    
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def get_person_status():
    """
    Polls Frigate API and calculates CURRENT state.
    Returns: 'WORKING', 'RESTING', 'AWAY'
    """
    try:
        # Use events endpoint with in_progress=1 to get current status
        url = f"{FRIGATE_URL}/api/events"
        params = {
            "camera": CAMERA_NAME,
            "label": "person", 
            "in_progress": 1,
            "limit": 5
        }
        
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            events = response.json()
            
            if not events:
                return 'AWAY'
            
            for event in events:
                # Get the latest known location (foot point)
                data = event.get('data', {})
                path_data = data.get('path_data', [])
                
                if path_data:
                    # Last point in path_data is the current location [x, y]
                    last_point = path_data[-1]
                    # Format is [[x, y], timestamp]
                    if len(last_point) >= 1:
                        coords = last_point[0]
                        current_x, current_y = coords[0], coords[1]
                        
                        # Check Point against Polygons
                        # User Logic:
                        # Desk -> WORKING
                        # Bed -> RESTING
                        # Else (Room) -> AWAY
                        if is_point_in_polygon(current_x, current_y, ZONES['desk']):
                            return 'WORKING'
                        if is_point_in_polygon(current_x, current_y, ZONES['bed']):
                            return 'RESTING'

            # If detected but not in zones (Room) -> AWAY per user request
            return 'AWAY' 
                
    except Exception as e:
        print(f"Error polling Frigate: {e}")
        return 'ERROR'
        
    return 'AWAY'

def main():
    print(f"Starting Activity Tracker via SQLite for {CAMERA_NAME}...")
    init_db()
    
    try:
        while True:
            current_status = get_person_status()
            
            # Log to SQLite
            if current_status != 'ERROR':
                log_state(current_status)
            
            # Print status to console (optional, for verification)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Status: {current_status}")
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()

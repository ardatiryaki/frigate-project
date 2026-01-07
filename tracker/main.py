import requests
import time
import json
from datetime import datetime

# Configuration
FRIGATE_URL = "http://localhost:5001"
CAMERA_NAME = "tapo_c222"
POLL_INTERVAL = 5  # seconds
STATS_FILE = "daily_stats.json"

# Hardcoded zones from config for robustness (normalized 0-1)
ZONES = {
    'desk': [0.684,0.714,0.894,0.865,0.918,1,0.58,1,0.594,0.846],
    'bed': [0.283,0.654,0.501,0.681,0.415,1,0.03,1,0.135,0.822]
}

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
    Polls Frigate API and calculates CURRENT zone based on latest coordinates.
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
                return 'away'
            
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
                        if is_point_in_polygon(current_x, current_y, ZONES['bed']):
                            return 'bed'
                        if is_point_in_polygon(current_x, current_y, ZONES['desk']):
                            return 'desk'

            # If person detected but geometry check fails (room)
            return 'room' 
                
    except Exception as e:
        print(f"Error polling Frigate: {e}")
        return 'error'
        
    return 'away'


def load_stats():
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"date": str(datetime.now().date()), "desk": 0, "bed": 0, "away": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def main():
    print(f"Starting Activity Tracker for {CAMERA_NAME}...")
    stats = load_stats()
    current_date = str(datetime.now().date())
    
    # Reset stats if new day
    if stats.get("date") != current_date:
        print("New day detected, resetting stats.")
        stats = {"date": current_date, "desk": 0, "bed": 0, "away": 0}

    while True:
        status = get_person_status()
        
        if status in stats:
            stats[status] += POLL_INTERVAL
            
        # Verify date change during run
        if str(datetime.now().date()) != stats["date"]:
             stats = {"date": str(datetime.now().date()), "desk": 0, "bed": 0, "away": 0}
             
        save_stats(stats)
        
        # Simple log
        print(f"Status: {status.upper()} | Desk: {stats['desk']}s | Bed: {stats['bed']}s | Away: {stats['away']}s")
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

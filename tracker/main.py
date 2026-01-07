import requests
import time
import json
from datetime import datetime

# Configuration
FRIGATE_URL = "http://localhost:5001"
CAMERA_NAME = "tapo_c222"
POLL_INTERVAL = 5  # seconds
STATS_FILE = "daily_stats.json"

def get_person_status():
    """
    Polls Frigate API to check if a person is in 'desk' or 'bed' zone.
    Returns: 'desk', 'bed', 'away'
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
        
        # Add timeout to prevent hanging
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            events = response.json()
            
            if not events:
                return 'away'
            
            # Check all active events for zones
            # Priority: Desk > Bed > Room
            for event in events:
                current_zones = event.get('zones', [])
                if 'bed' in current_zones:
                    return 'bed'
                if 'desk' in current_zones:
                    return 'desk'
            
            # If person detected but not in desk/bed zones
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

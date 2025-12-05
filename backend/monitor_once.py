import json
import os
import requests
import base64
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
TELERIVET_API_KEY = os.environ.get('TELERIVET_API_KEY', '')
TELERIVET_PROJECT_ID = os.environ.get('TELERIVET_PROJECT_ID', '')
DATA_SOURCE_FILE = 'river_data.json' 

# Thresholds
DISCHARGE_THRESHOLD = 100000 

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase Credentials")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def send_sms(to_number, message):
    if not TELERIVET_API_KEY or not TELERIVET_PROJECT_ID:
        print("Missing Telerivet Credentials")
        return

    url = f"https://api.telerivet.com/v1/projects/{TELERIVET_PROJECT_ID}/messages/send"
    auth_string = f"{TELERIVET_API_KEY}:"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    data = {
        "to_number": to_number,
        "content": message
    }

    try:
        response = requests.post(
            url,
            data=data,
            headers={"Authorization": f"Basic {auth_encoded}"}
        )
        print(f"✓ Sent SMS to {to_number}: Status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Failed to send SMS to {to_number}: {e}")
        return False

def check_river_data(supabase):
    try:
        if not os.path.exists(DATA_SOURCE_FILE):
            print(f"✗ {DATA_SOURCE_FILE} not found.")
            return

        with open(DATA_SOURCE_FILE, 'r') as f:
            data = json.load(f)

        # Get the latest entry with data
        latest_entry = None
        for entry in data:
            if entry.get('stations'):
                latest_entry = entry
                break
        
        if not latest_entry:
            print("✗ No station data found.")
            return

        print(f"📊 Checking data for date: {latest_entry.get('date')}")
        stations = latest_entry.get('stations', {})
        alerts_sent = 0

        for station_name, metrics in stations.items():
            discharge_vals = []
            for k, v in metrics.items():
                if "DISCHARGE" in k and isinstance(v, (int, float)):
                    discharge_vals.append(v)
            
            max_discharge = max(discharge_vals) if discharge_vals else 0
            
            if max_discharge > DISCHARGE_THRESHOLD:
                print(f"⚠️  HIGH DISCHARGE at {station_name}: {max_discharge} cusecs")
                count = notify_users(supabase, station_name, max_discharge)
                alerts_sent += count
            else:
                print(f"✓ {station_name}: {max_discharge} cusecs (Normal)")

        print(f"\n📨 Total alerts sent: {alerts_sent}")

    except Exception as e:
        print(f"✗ Error checking river data: {e}")

def notify_users(supabase, station_name, discharge_level):
    if not supabase:
        return 0

    try:
        # Fetch users interested in this station
        response = supabase.table('users').select("*").eq('station', station_name).execute()
        users = response.data
        
        if not users:
            print(f"  ℹ️  No users registered for {station_name}")
            return 0

        sent_count = 0
        msg = f"ALERT: High water level detected at {station_name} ({discharge_level} cusecs). Please take necessary precautions."
        
        for user in users:
            if send_sms(user['phone'], msg):
                sent_count += 1
        
        print(f"  ✓ Sent {sent_count}/{len(users)} alerts for {station_name}")
        return sent_count
            
    except Exception as e:
        print(f"✗ Error fetching users from Supabase: {e}")
        return 0

def main():
    print("=" * 60)
    print("🌊 FLOOD MONITORING SYSTEM - Single Run")
    print("=" * 60)
    
    supabase = get_supabase_client()
    
    if not supabase:
        print("✗ Cannot proceed without Supabase connection")
        return
    
    check_river_data(supabase)
    
    print("=" * 60)
    print("✓ Monitoring complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

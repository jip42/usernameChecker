import requests
import time
from datetime import datetime
import os # To easily save the log file in your current directory

# --- Configuration ---
HANDLE_TO_CHECK = "@YourDesiredHandleName"  # <-- **EDIT THIS TO YOUR TARGET HANDLE**
CHECK_INTERVAL_SECONDS = 24 * 60 * 60      # Check once per day (24 hours)

# --- Core Logic ---

def is_handle_available(handle):
    """
    Checks YouTube handle availability using the HTTP status code.
    - A 200 code usually means the page exists (handle is TAKEN).
    - A 404 code usually means the page does not exist (handle is FREE).
    """
    url = f"https://www.youtube.com/{handle}"
    
    # Simple requests.head() is faster as it doesn't download the full page content
    try:
        # Use a common User-Agent to mimic a regular browser and avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, timeout=15, headers=headers)
        status_code = response.status_code

        # YouTube uses 200 (OK) for a taken handle page.
        # It uses 404 (Not Found) for an unavailable page.
        if status_code == 404:
            return True, f"Status {status_code}: Handle is **FREE**!"
        elif status_code == 200:
            return False, f"Status {status_code}: Handle is TAKEN."
        else:
            return False, f"Status {status_code}: Unknown response. Check manually."

    except requests.exceptions.RequestException as e:
        return False, f"ERROR: Connection failed ({e})"

def run_checker():
    """Runs the check and logs the result."""
    log_file_name = f"handle_check_{HANDLE_TO_CHECK.replace('@', '')}.log"
    
    available, message = is_handle_available(HANDLE_TO_CHECK)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] Checking {HANDLE_TO_CHECK} - Result: {message}"
    
    # Print and save the result
    print(log_entry)
    with open(log_file_name, "a") as f:
        f.write(log_entry + "\n")
        
    if available:
        print("\n*** SUCCESS! The handle is available. Stopping checker. ***")
    
    return available

if __name__ == "__main__":
    print(f"--- Simple YouTube Handle Checker ({HANDLE_TO_CHECK}) ---")
    
    # Loop indefinitely, checking at the set interval
    while True:
        if run_checker():
            break # Exit the loop if the handle is free
        
        print(f"Waiting for {CHECK_INTERVAL_SECONDS/3600} hours until the next check...")
        time.sleep(CHECK_INTERVAL_SECONDS)
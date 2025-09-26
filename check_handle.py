import requests
import os
from datetime import datetime
from win10toast import ToastNotifier

# --- Configuration ---
HANDLE_TO_CHECK = "@YourDesiredHandleName"  # <-- **EDIT THIS TO YOUR TARGET HANDLE**
LOG_FILE_NAME = f"handle_check_{HANDLE_TO_CHECK.replace('@', '')}.log"

# --- Core Logic ---

def is_handle_available(handle):
    """Checks YouTube handle availability using the HTTP status code."""
    url = f"https://www.youtube.com/{handle}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, timeout=15, headers=headers)
        status_code = response.status_code

        if status_code == 404:
            return True, f"Status {status_code}: Handle is **FREE**!"
        elif status_code == 200:
            return False, f"Status {status_code}: Handle is TAKEN."
        else:
            return False, f"Status {status_code}: Unknown response."

    except requests.exceptions.RequestException as e:
        return False, f"ERROR: Connection failed ({e})"

def notify_user(title, message, duration=5):
    """Sends a Windows Toast Notification."""
    toaster = ToastNotifier()
    toaster.show_toast(
        title, 
        message, 
        duration=duration, 
        icon_path=None # Can add an icon path here if desired
    )

def run_checker_once():
    """Runs the check, logs the result, and sends a notification if free."""
    available, message = is_handle_available(HANDLE_TO_CHECK)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] Checking {HANDLE_TO_CHECK} - Result: {message}"
    
    # Print and save the result
    print(log_entry)
    with open(LOG_FILE_NAME, "a") as f:
        f.write(log_entry + "\n")
        
    if available:
        notify_user("SUCCESS! YouTube Handle FREE!", 
                    f"The handle {HANDLE_TO_CHECK} is now available! Check YouTube immediately.", 
                    duration=10)
    else:
        # Optionally send a 'still taken' notification, but usually not needed for a clean solution
        pass
    
    return available

if __name__ == "__main__":
    print(f"--- Running Single YouTube Handle Check for {HANDLE_TO_CHECK} ---")
    run_checker_once()
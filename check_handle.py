import requests
import os
from datetime import datetime
from win10toast import ToastNotifier

# --- Configuration ---
HANDLE_TO_CHECK = "@shayon"  # <--- **YOUR TARGET HANDLE**
LEGACY_NAME_CHECK = "shayon" # <--- The handle without the '@' symbol
LOG_FILE_NAME = f"handle_check_{LEGACY_NAME_CHECK}.log"

# --- Core Logic ---

def check_url_status(url):
    """Checks the HTTP status code for a given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use HEAD request for speed, as we only need the status code
        response = requests.head(url, timeout=15, headers=headers)
        return response.status_code
    except requests.exceptions.RequestException as e:
        # Return a code that indicates a connection issue
        return 503 # Service Unavailable or similar error

def is_handle_available(handle, legacy_name):
    """
    Checks both the modern @handle URL and the common legacy URLs.
    
    Returns: (boolean_available, status_message)
    """
    
    # 1. Check Modern @Handle URL
    modern_url = f"https://www.youtube.com/{handle}"
    modern_status = check_url_status(modern_url)
    
    if modern_status == 404:
        modern_message = f"Modern handle URL ({modern_url}) returned **404 (Free)**."
        is_modern_free = True
    elif modern_status == 200:
        return False, f"Modern handle URL ({modern_url}) returned **200 (Taken)**."
    else:
        modern_message = f"Modern handle URL returned Status {modern_status} (Connection/Unknown Error)."
        is_modern_free = False # Treat non-404/200 as potentially taken or an error

    # 2. Check Legacy /user/ and /c/ URLs (Only if the modern check passes or is inconclusive)
    legacy_urls = [
        f"https://www.youtube.com/user/{legacy_name}",
        f"https://www.youtube.com/c/{legacy_name}"
    ]
    
    for url_type, legacy_url in zip(['/user/', '/c/'], legacy_urls):
        legacy_status = check_url_status(legacy_url)
        if legacy_status == 200:
            return False, f"Legacy {url_type} URL ({legacy_url}) returned **200 (Taken)**. Handle is reserved."
        
        # Log the legacy check result, but 404 is the expected result if the handle is free
        # We don't need to exit on 404 here, as that's good news.

    # 3. Final Determination
    if is_modern_free:
        # All checks point to the handle URL not being actively used
        # We still know the API check in YouTube Studio might say 'taken' due to cooldown,
        # but the script will notify if the public URLs are all clear.
        return True, "All public URLs (Modern, /user/, /c/) returned **404 (Free)**."
    
    # If the modern check was an error (e.g., 503) and legacy checks didn't show 200.
    return False, f"Check Inconclusive. Modern status: {modern_status}. Legacy URLs look clear."


def notify_user(title, message, duration=5):
    """Sends a Windows Toast Notification."""
    toaster = ToastNotifier()
    toaster.show_toast(
        title, 
        message, 
        duration=duration, 
        icon_path=None
    )

def run_checker_once():
    """Runs the full check, logs the result, and sends a notification if free."""
    
    # Check both the handle and the name without the '@'
    available, message = is_handle_available(HANDLE_TO_CHECK, LEGACY_NAME_CHECK)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] Checking {HANDLE_TO_CHECK} - Result: {message}"
    
    # Print and save the result
    print(log_entry)
    with open(LOG_FILE_NAME, "a") as f:
        f.write(log_entry + "\n")
        
    if available:
        # Only notify on SUCCESS (i.e., when all URLs are 404)
        notify_user("SUCCESS! YouTube Handle FREE!", 
                    f"The handle {HANDLE_TO_CHECK} is now available! Try claiming it immediately.", 
                    duration=10)
    else:
        # Optional: Notify on critical failure or known 'Taken' status
        if "200 (Taken)" in message:
            notify_user("Handle Check: Still Taken", 
                        f"Status 200 was found. Still reserved or in use.", 
                        duration=3)
        # We generally suppress the notification on 404 (but API still says taken) to avoid spam.
        pass

if __name__ == "__main__":
    run_checker_once()
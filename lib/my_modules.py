# We've all shoved our toys under our beds, haven't we?
import time
import random

def gaussian_sleep(mu, sigma):
    wait_sec = random.gauss(mu, sigma)
    wait_sec = mu if (wait_sec <= 0) else wait_sec
    return time.sleep(wait_sec)

def print_progress(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.2f}%)")

def persistent_get(session, url, max_retries):
    try:
        return session.get(url)
    except:
        while max_retries != 0:
            max_retries -= 1
            try:
                res = session.get(url)
                max_retries = 0
                return res
            except:
                print(f"!!!Retried to get {url}\nAttempts left: {max_retries}")

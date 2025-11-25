# STRESS TEST SCRIPT 

import threading
import requests
import time

URL = "http://bee-data-api.onrender.com/api/location-data/?lat=44.56&long=-123.26"

def make_request(i):
    try:
        print(f"Thread {i}: Sending request...")
        response = requests.get(URL)
        print(f"Thread {i}: Status {response.status_code}")
    except Exception as e:
        print(f"Thread {i}: Failed - {e}")

threads = []
start_time = time.time()

for i in range(20):
    t = threading.Thread(target=make_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Finished in {time.time() - start_time} seconds")
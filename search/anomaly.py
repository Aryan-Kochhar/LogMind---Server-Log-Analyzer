import sys
import os

filepath = r"Log File Path"

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))

from log_parser import parse_file

CRITICAL_KEYWORDS = ["timeout", "out of memory", "deadlock", "connection refused"]
WINDOW_SIZE = 10
ERROR_THRESHOLD = 3

def detect_anomalies(logs):
    anomalies = []
    
    # Check critical keywords
    for log in logs:
        for keyword in CRITICAL_KEYWORDS:
            if keyword in log["message"].lower():
                anomalies.append(log)
    
    # Sliding window error spike detection
    for i in range(len(logs)):
        window = logs[i:i+WINDOW_SIZE]
        error_count = len([log for log in logs if log["level"]== "ERROR"])
        if error_count > ERROR_THRESHOLD:
            for l in window:
                if l["level"] == "ERROR" and l not in anomalies:
                    anomalies.append(l)
    
    return anomalies

if __name__ == "__main__":
    logs = parse_file(filepath)
    results = detect_anomalies(logs)
    for r in results:
        print(r)
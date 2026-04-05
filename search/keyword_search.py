import sys
import os

filepath = r"Log File Path"

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))

from log_parser import parse_file

def search(logs,keyword):
    l = []
    for log in logs:
        if (keyword in log["message"]) or (keyword in log["level"]):
            l.append(log)
    return l

if __name__ == "__main__":
    logs = parse_file(filepath)
    results = search(logs,"connection")

    for r in results:
        print(r)
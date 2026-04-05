import re

filepath = r"Log File Path"

def parse_line(line):
    pattern1 = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<message>.+)"
    pattern2 = r'(?P<ip>\d+\.\d+\.\d+\.\d+) \- \- \[(?P<timestamp>\d{2}\/\w+\/\d{4}:\d{2}:\d{2}:\d{2}) [^\]]+\] "(?P<request>[^"]+)" (?P<status>\d{3})'
    
    match = re.match(pattern1,line)
    if (match):
        return {
            "timestamp":f"{match.group("date")} {match.group("time")}",
            "level":match.group("level"),
            "message": match.group("message")
            }
    match = re.match(pattern2,line)
    if (match):
        status = int(match.group("status"))
        if status >= 500:
            level = "ERROR"
        elif status >= 400:
            level = "WARN"
        else:
            level = "INFO"
        return {
            "timestamp": match.group("timestamp"),
            "level": level,
            "message": f'{match.group("request")} - {match.group("status")}'
        }
    return None

def parse_file(filepath):
    l = []
    with open(filepath,"r") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                l.append(parsed)
            #else:
            #    print("NO MATCH:", line[:80])  # print first 80 chars of unmatched lines
    return l
if __name__ == "__main__":
    logs = parse_file(filepath)
    for log in logs:
        print(log)
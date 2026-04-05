import sys
import os
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rag'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'search'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'llm'))

from log_parser import parse_file
from mongo_store import store_logs, collection
from retriever import retrieve
from keyword_search import search
from anomaly import detect_anomalies
from llm_client import ask_llm

def main():
    print("Helooo I'm LogMind CLI!")
    
    filepath = input("Enter path to the log file: ")
    print("Parsing the logs...")
    logs = parse_file(filepath)
    print(f"Loaded {len(logs)} log entries")
    
    count = collection.count_documents({})
    if count == 0:
        print("Storing embeddings in MongoDB...")
        store_logs(logs)
    else:
        print(f"Using {count} existing logs from MongoDB")
    
    print("\nRunning anomaly detection...")
    anomalies = detect_anomalies(logs)
    if anomalies:
        print(f"{len(anomalies)} anomalies detected.")
        for a in anomalies:
            print(f"[{a['level']}] {a['message']}")
    else:
        print("No anomalies detected.")
    
    print("Hi! I'm the goated chat, ask me anything dipshit!")
    print("Commands for yours truly: 'search <keyword>' or just ask a question. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Mi lord's command: ").strip()
        if user_input.lower() == "exit":
            break
        elif user_input.lower().startswith("search "):
            keyword = user_input[7:]
            if keyword.upper() in ["ERROR", "WARN", "INFO"]:
                results = [l for l in logs if l["level"] == keyword.upper()]
            else:
                results = search(logs, keyword)
            print(f"Found {len(results)} matches:")
            for r in results:
                print(f" [{r['level']}] {r['timestamp']} - {r['message']}")
        elif user_input.lower() == "stats":
            errors = [l for l in logs if l["level"] == "ERROR"]
            warns = [l for l in logs if l["level"] == "WARN"]
            infos = [l for l in logs if l["level"] == "INFO"]
            print(f"\nEntire Log Summary:")
            print(f"  ERROR : {len(errors)}")
            print(f"  WARN  : {len(warns)}")
            print(f"  INFO  : {len(infos)}")
            print(f"  TOTAL : {len(logs)}\n")
        elif user_input.lower().startswith("count "):
            keyword = user_input[6:]
            results = search(logs, keyword)
            print(f"\n Found {len(results)} logs containing '{keyword}'\n")
        elif user_input.lower().startswith("summary "):
            date = user_input[8:]
            day_logs = [l for l in logs if date in l["timestamp"]]
            if not day_logs:
                print(f"No logs found for {date}")
            else:
                print(f"Found {len(day_logs)} logs for {date}, analyzing...")
                answer = ask_llm(f"Summarize what happened on {date}", day_logs[:20])
                print(f"\nWatashiwa thinks that: {answer}\n")
        elif user_input.lower().startswith("top errors"):
            counts = {}
            for log in logs:
                if log['level'] in ["ERROR","WARN"]:
                    counts[log["message"]] = counts.get(log["message"], 0) + 1
            # sorting count in desc
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            # print top 5
            for message, count in sorted_counts[:5]:
                print(f"{count}x - {message}")
        elif user_input.lower() == "debug":
            print(logs[0])
            errors = [l for l in logs if l["level"] == "WARN"]
            print(f"WARN count: {len(errors)}")
        elif user_input.lower().startswith("export"):
            parts = user_input.split(" ", 1)
            if len(parts) == 1:
                filtered = logs
            else:
                keyword = parts[1].upper()
                if keyword in ["ERROR", "WARN", "INFO"]:
                    filtered = [l for l in logs if l["level"] == keyword]
                else:
                    filtered = search(logs, parts[1])
            filename = input("Enter filename (blah-blah.csv): ")
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "message"])
                writer.writeheader()
                clean_logs = [{"timestamp": l["timestamp"], "level": l["level"], "message": l["message"]} for l in filtered]
                writer.writerows(clean_logs)
            print(f"Exported {len(filtered)} logs to {filename}")
        else:
            context = retrieve(user_input)
            answer = ask_llm(user_input,context)
            print(f"Watashiwa thinks that: {answer}\n")

if __name__ == "__main__":
    main() 
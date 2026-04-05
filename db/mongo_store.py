from dotenv import load_dotenv
import os
from pymongo import MongoClient
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'embeddings'))
from embedder import embed_text

load_dotenv()
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("Connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

db = client["log_analyzer"]
collection = db["logs"]

def store_logs(logs):
    collection.delete_many({})  # clear old logs on each run
    for log in logs:
        log["embedding"] = embed_text(log["message"])
        collection.insert_one(log)
    print(f"Stored {len(logs)} logs in MongoDB")

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))
    from log_parser import parse_file

    logs = parse_file(r"C:\Programming\Projects\Server Log Analyzer\sample.log")
    store_logs(logs)
from dotenv import load_dotenv
import os
import time
from pymongo import MongoClient
from pymongo.errors import AutoReconnect
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'embeddings'))
from embedder import embed_text, embed_texts

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

INSERT_BATCH = 1000
WRITE_RETRIES = 3
RETRY_WAIT = 2

def write_all(logs):
    # every attempt starts from an empty collection, so a retry cannot leave
    # duplicates. one insert_many for 10k embeddings is also ~30MB on the wire,
    # long enough for the TLS connection to drop, so send it in chunks
    collection.delete_many({})
    for i in range(0, len(logs), INSERT_BATCH):
        collection.insert_many(logs[i:i + INSERT_BATCH])

def store_logs(logs, source=None):
    collection.delete_many({})  # clear old logs on each run
    if not logs:
        return
    if source:
        source = os.path.abspath(source)
    embeddings = embed_texts([log["message"] for log in logs])
    for log, embedding in zip(logs, embeddings):
        log["embedding"] = embedding
        log["source"] = source

    for attempt in range(1, WRITE_RETRIES + 1):
        try:
            write_all(logs)
            print(f"Stored {len(logs)} logs in MongoDB")
            return
        except AutoReconnect as e:
            print(f"Write failed (attempt {attempt} of {WRITE_RETRIES}): {e}")
            if attempt == WRITE_RETRIES:
                # a half-written collection still looks complete to
                # already_stored(), so clear it rather than leave it partial
                collection.delete_many({})
                raise
            time.sleep(RETRY_WAIT)

def already_stored(source):
    # the collection holds one file at a time, so checking the row count alone
    # would reuse another file's embeddings - match on the source path instead
    return collection.count_documents({"source": os.path.abspath(source)}) > 0

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))
    from log_parser import parse_file

    path = r"C:\Programming\Projects\Server Log Analyzer\sample.log"
    logs = parse_file(path)
    store_logs(logs, path)
from dotenv import load_dotenv
import os
from pymongo import MongoClient
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

    # one insert_many for 10k embeddings is ~30MB on the wire and long enough
    # for the TLS connection to drop halfway, so send it in chunks
    try:
        for i in range(0, len(logs), INSERT_BATCH):
            collection.insert_many(logs[i:i + INSERT_BATCH])
    except Exception:
        # a half-written collection still looks complete to already_stored(),
        # so clear it and let the next run re-ingest from scratch
        collection.delete_many({})
        raise
    print(f"Stored {len(logs)} logs in MongoDB")

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
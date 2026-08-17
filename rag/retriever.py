import sys
import os
# taking user question, embedding using same model and asking
# mongodb to find most similar entry and return the logs as context

sys.path.append(os.path.join(os.path.dirname(__file__),'..','embeddings'))
sys.path.append(os.path.join(os.path.dirname(__file__),'..','db'))

from embedder import embed_text
from mongo_store import collection

def check_search_ready():
    # $vectorSearch returns an empty list instead of erroring when the index is
    # missing, so an empty result needs explaining rather than passing through
    if collection.count_documents({}) == 0:
        raise RuntimeError("No logs stored yet - load a log file first.")

    ready = [i["name"] for i in collection.list_search_indexes() if i.get("queryable")]
    if "vector_index" not in ready:
        raise RuntimeError(
            "Vector index 'vector_index' is missing or still building. "
            "It does not survive an Atlas cluster pause - recreate it on the "
            "logs collection (see README step 5) and wait for it to go READY."
        )

def retrieve(query, top_k=3):
    query_embedding = embed_text(query)

    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": 20
            }
        }
    ])
    
    logs = list(results)
    if not logs:
        check_search_ready()

    query_lower = query.lower()
    if any(word in query_lower for word in ["error", "fail", "warn", "problem", "issue", "least", "most", "common", "frequent", "top"]):
        filtered = [l for l in logs if l["level"] in ["ERROR", "WARN"]]
        if filtered:
            return filtered[:top_k]
    
    return logs[:top_k]

if __name__=="__main__":
    results = retrieve("memory")
    for r in results:
        print(r["level"],"-",r["message"])


import sys
import os
# taking user question, embedding using same model and asking
# mongodb to find most similar entry and return the logs as context

sys.path.append(os.path.join(os.path.dirname(__file__),'..','embeddings'))
sys.path.append(os.path.join(os.path.dirname(__file__),'..','db'))

from embedder import embed_text
from mongo_store import collection

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
    
    query_lower = query.lower()
    if any(word in query_lower for word in ["error", "fail", "warn", "problem", "issue"]):
        filtered = [l for l in logs if l["level"] in ["ERROR", "WARN"]]
        if filtered:
            return filtered[:top_k]
    
    return logs[:top_k]

if __name__=="__main__":
    results = retrieve("memory")
    for r in results:
        print(r["level"],"-",r["message"])


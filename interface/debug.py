import sys
sys.path.append(r"C:\Programming\Projects\Server Log Analyzer\rag")
sys.path.append(r"C:\Programming\Projects\Server Log Analyzer\embeddings")  
sys.path.append(r"C:\Programming\Projects\Server Log Analyzer\db")
from retriever import retrieve

results = retrieve("what are the most common errors", top_k=3)
for r in results:
    print(r["level"], "-", r["message"])
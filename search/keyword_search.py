import sys
import os

filepath = r"Log File Path"

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))

from log_parser import parse_file

# phrasings that ask about the rarest errors rather than the most repeated ones
RAREST_PHRASES = ["least common", "least frequent", "least error", "fewest", "rarest"]

# "at least" is deliberately not here - it shows up in questions that are not
# about counts at all
AGGREGATE_PHRASES = RAREST_PHRASES + ["most common", "most frequent", "top error",
                                      "biggest error", "how many", "which error",
                                      "what errors"]

def search(logs,keyword):
    l = []
    for log in logs:
        if (keyword in log["message"]) or (keyword in log["level"]):
            l.append(log)
    return l

def is_aggregate(question):
    # "what are the most common errors?" is a counting question, not a
    # similarity one - vector search ranks by meaning and misses the counts
    q = question.lower()
    return any(phrase in q for phrase in AGGREGATE_PHRASES)

def wants_rarest(question):
    q = question.lower()
    return any(phrase in q for phrase in RAREST_PHRASES)

def top_errors(logs, limit=5, rarest=False):
    counts = {}
    for log in logs:
        if log["level"] in ["ERROR", "WARN"]:
            counts[log["message"]] = counts.get(log["message"], 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=not rarest)
    return ranked[:limit]

if __name__ == "__main__":
    logs = parse_file(filepath)
    results = search(logs,"connection")

    for r in results:
        print(r)
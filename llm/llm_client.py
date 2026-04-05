import litellm

def ask_llm(question,context_logs):
    #formatting the logs as the context
    
    context = "\n".join([
        f"[{log['level']}] [{log['timestamp']}-{log['message']}]"
        for log in context_logs
    ])
    
    prompt = f"""You are an expert server log analysis assistant.

    You are given a set of log entries. Your job is to analyze ONLY the provided logs and answer the question.

    --- LOG ENTRIES ---
    {context}
    -------------------

    QUESTION:
    {question}

    INSTRUCTIONS:
    1. Base your answer strictly on the logs. Do NOT assume anything not present.
    2. If the logs are insufficient, explicitly say: "Insufficient information from logs."
    3. Identify relevant log lines before reasoning.
    4. Focus on root cause, not just symptoms.
    5. Be concise, technical, and precise.

    OUTPUT FORMAT:
    - Root Cause: <most likely cause>
    - Evidence: <specific log lines or patterns>
    - Explanation: <brief technical reasoning>
    - Confidence: <High / Medium / Low>
    """

    response = litellm.completion(
        model="ollama/qwen2.5:14b",
        messages=[{"role":"user","content":prompt}],
        api_base="http://localhost:11434" 
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    fake_logs = [{"level": "ERROR", "timestamp": "2024-01-15 08:02:01", "message": "Database connection failed"}]
    print(ask_llm("Why is the database failing?", fake_logs))
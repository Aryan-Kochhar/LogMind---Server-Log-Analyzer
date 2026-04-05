# LogMind - AI Server Log Analyzer

## What is this?
LogMind lets you chat with your server logs — upload any log file and ask questions in plain English. It can summarize the entirety of your logs, search any error and display where the particular kind of error is present. 

## Tech Stack
[list the technologies you used]
1. python and regex (log parsing)
2. sentence-transformers (embeddings)
3. MongoDB Atlas (vector storage + search)
4. Ollama + DeepSeek/Qwen (local LLM)
5. litellm (model-agnostic LLM interface)
6. CLI (interface)

## Project Structure
Server Log Analyser/
    db -> mongo_store.py
    embeddings -> embedder.py
    interface -> 
        cli.py
        cliLoaded.py (if logs already present in MongoDB)
    llm -> llm_client.py
    rag -> retriever.py
    search -> 
        anomaly.py
        keyword_search.py
    logs/
        apachelogs.log
        sample.log
    .env
    .gitignore
    requirements.txt
    README.md       



## How to Run
1. Clone the repo
2. Create a virtual environment: `python -m venv env`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with your MongoDB URI...

Q. What do I need to install first?
    install sentence-tranformers litellm and regex
Q. What do they need to set up? (MongoDB, Ollama, .env)
    setup mongodb cluster, search_index, and mongodbURI, download ollama model and run it (any offline llm), and setup ollama's url 
Q. What command do they run?
    after all files, just run cli.py if nologs in cluster, if logs present just run cliLoaded.py

## Features
1. Can give stats of the entire log file, counts of each kind of keyword
2. Can find out the most common error
3. Can search according to message/error keywords
4. Export the file in csv 


## Example Queries
[example questions you can ask]
1. "stats" (displays all stats)
2. "count 'keyword' "(any error)
3. "what are the most common errors?"
4. "search errors" (warn,404,200,500 etc)
5. "what happened on 17/May/2015?"
6. "are there any security threats?"
7. "export", "export 404", "export warn" 

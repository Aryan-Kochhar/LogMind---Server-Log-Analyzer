import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rag'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'llm'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'search'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'search'))

from mongo_store import store_logs, collection
from retriever import retrieve
from llm_client import ask_llm
from keyword_search import search

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))
from log_parser import parse_file

st.title("LogMind - AI Server Log Analyzer")

uploaded_file = st.file_uploader("Upload a log file", type=["log", "txt"])

if uploaded_file:
    # save it temporarily so parse_file can read it
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    
    
    
    logs = parse_file(temp_path)
    with st.spinner("Storing embeddings in MongoDB..."):
        count = collection.count_documents({})
        if count == 0:
            store_logs(logs)
    st.success(f"✅ Loaded {len(logs)} log entries")
    
    st.subheader("📊 Log Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    errors = len([l for l in logs if l["level"] == "ERROR"])
    warns  = len([l for l in logs if l["level"] == "WARN"])
    infos  = len([l for l in logs if l["level"] == "INFO"])
    
    col1.metric("Total", len(logs))
    col2.metric("Errors 🔴", errors)
    col3.metric("Warnings 🟡", warns)
    col4.metric("Info 🟢", infos)
    
    if errors > 0:
        st.subheader("🔥 Top Errors")
        counts = {}
        for log in logs:
            if log["level"] in ["ERROR", "WARN"]:
                counts[log["message"]] = counts.get(log["message"], 0) + 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for msg, count in sorted_counts:
            st.write(f"`{count}x` — {msg}")
    
    # Anomaly Detection
    st.subheader("⚠️ Anomaly Detection")
    from anomaly import detect_anomalies
    
    anomalies = detect_anomalies(logs)
    if anomalies:
        st.warning(f"Detected {len(anomalies)} anomalous log entries!")
        st.dataframe(anomalies, use_container_width=True)
    else:
        st.success("No anomalies detected!")
    
    st.subheader("📋 Log Viewer")
    
    # filter by level
    level_filter = st.selectbox("Filter by level", ["ALL", "ERROR", "WARN", "INFO"])
    search_term = st.text_input("Search logs")
    
    filtered = logs
    if level_filter != "ALL":
        filtered = [l for l in filtered if l["level"] == level_filter]
    if search_term:
        filtered = [l for l in filtered if search_term.lower() in l["message"].lower()]
    
    st.write(f"Showing {len(filtered)} entries")
    st.dataframe(filtered, use_container_width=True)
    
# Export
    st.subheader("📤 Export")
    if st.button("Export filtered logs as CSV"):
        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "level", "message"])
        writer.writeheader()
        clean = [{"timestamp": l["timestamp"], "level": l["level"], "message": l["message"]} for l in filtered]
        writer.writerows(clean)
        st.download_button(
            label="Download CSV",
            data=output.getvalue(),
            file_name="logs_export.csv",
            mime="text/csv"
        )
    
    st.subheader("💬 Chat with your logs")
    # initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # chat input
    user_input = st.chat_input("Ask anything about your logs...")
    if user_input:
    # show user message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # get answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                context = retrieve(user_input)
                answer = ask_llm(user_input, context)
                st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
import os
import requests
import pandas as pd
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Agentic CS Support", layout="wide")

st.title("Agentic Customer Service Support System")

tabs = st.tabs(["🧑‍💼 Representative View", "📊 Manager Dashboard"])

def confidence_badge(conf: int):
    if conf >= 80:
        st.success(f"Confidence: {conf}%")
    elif conf >= 60:
        st.warning(f"Confidence: {conf}%")
    else:
        st.error(f"Confidence: {conf}%")

with tabs[0]:
    st.subheader("Representative View")

    colA, colB = st.columns([1, 2], gap="large")
    with colA:
        rep_id = st.text_input("Rep ID", value="rep-1")
        question = st.text_area("Customer / Rep question", height=130, placeholder="Type the rep's raw question here...")
        ask = st.button("Ask", type="primary", use_container_width=True)

        st.caption("Tip: Use messy, real-world language. The Reformulation Agent will translate it into a clean search query.")

    with colB:
        # When Ask is clicked, call the backend and cache the latest result
        if ask and question.strip():
            try:
                r = requests.post(f"{BACKEND_URL}/ask", json={"rep_id": rep_id, "question": question}, timeout=30)
                r.raise_for_status()
                st.session_state["last_result"] = r.json()
            except Exception as e:
                st.error(f"Backend error: {e}")
                st.stop()

        data = st.session_state.get("last_result")

        if data:
            st.markdown("### Answer")
            st.write(data["answer"])

            confidence_badge(int(data["confidence"]))

            with st.expander("🔎 Agent pipeline details"):
                st.write(f"**Intent:** {data['intent']}")
                st.code(data["reformulated_query"], language="text")
                st.write(f"**Latency:** {data['latency_ms']} ms")
                st.write("**Sources:** " + ", ".join(data["sources"]) if data["sources"] else "None")

            if data["sources"]:
                st.markdown("### Sources")
                for doc_id in data["sources"]:
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        if st.button(f"Open {doc_id}", key=f"open-{doc_id}"):
                            txt = requests.get(f"{BACKEND_URL}/source/{doc_id}", timeout=30).text
                            st.session_state[f"src-{doc_id}"] = txt
                    with c2:
                        st.caption("Shows full source document text (grounding).")

                for doc_id in data["sources"]:
                    if f"src-{doc_id}" in st.session_state:
                        st.markdown(f"#### {doc_id} (Full Document)")
                        st.code(st.session_state[f"src-{doc_id}"], language="markdown")

with tabs[1]:
    st.subheader("Manager Dashboard")

    try:
        stats = requests.get(f"{BACKEND_URL}/stats", timeout=30).json()
    except Exception as e:
        st.error(f"Backend error: {e}")
        st.stop()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Queries", stats["total_queries"])
    m2.metric("Avg Confidence", stats["avg_confidence"])
    m3.metric("Avg Latency (ms)", stats["avg_latency_ms"])

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### Queries per Rep")
        df_rep = pd.DataFrame(stats["per_rep"])
        if not df_rep.empty:
            st.dataframe(df_rep, use_container_width=True)
        else:
            st.info("No data yet. Ask a question in the Representative View.")

        st.markdown("### Most Asked Topics (Intent)")
        df_int = pd.DataFrame(stats["top_intents"])
        if not df_int.empty:
            st.bar_chart(df_int.set_index("intent")["cnt"])
        else:
            st.info("No data yet.")

    with col2:
        st.markdown("### Most Used Documents")
        df_docs = pd.DataFrame(stats["top_docs"])
        if not df_docs.empty:
            st.dataframe(df_docs, use_container_width=True)
        else:
            st.info("No data yet.")

        st.markdown("### Low Confidence Answers (< 60%)")
        df_low = pd.DataFrame(stats["low_confidence"])
        if not df_low.empty:
            st.dataframe(df_low, use_container_width=True)
        else:
            st.success("No low-confidence answers so far.")

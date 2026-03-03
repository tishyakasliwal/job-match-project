import streamlit as st
import json
from src.normalize import fetch_jobs_from_url, dedupe_jobs
from src.index_store import build_index
from src.match_agent import rank_jobs

st.set_page_config(page_title="Job Match Agent", layout="wide")
st.title("Job Postings RAG + Match Agent (ATS Board URLs)")

with st.sidebar:
    st.header("Inputs")
    board_urls = st.text_area(
        "Paste ATS board URLs (one per line)",
        value="https://api.lever.co/v0/postings/whoop"
    )
    preferences = st.text_area(
        "Preferences (location, role type, must-haves, etc.)",
        value="New grad / early career. Interested in ML/AI SWE or Data Scientist. Prefer NYC/Boston or Remote. Must-have: Python."
    )
    profile = st.text_area(
        "Your profile/resume text",
        value="Paste your resume text here..."
    )

if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "index" not in st.session_state:
    st.session_state.index = None

col1, col2 = st.columns([1,1])

with col1:
    if st.button("1) Fetch Jobs"):
        urls = [u.strip() for u in board_urls.splitlines() if u.strip()]
        all_jobs = []
        for u in urls:
            try:
                all_jobs.extend(fetch_jobs_from_url(u))
                #print(all_jobs)
            except Exception as e:
                st.warning(f"Failed to fetch {u}: {e}")
        all_jobs = dedupe_jobs(all_jobs)
        st.session_state.jobs = all_jobs
        st.success(f"Fetched {len(all_jobs)} job postings.")
    st.subheader("Fetched jobs preview")
    for j in st.session_state.jobs[:10]:
        st.write(f"**{j.company} — {j.title}**")
        st.caption(f"{j.location or 'Unknown'} • {j.source} • {j.url}")

with col2:
    if st.button("2) Build Index"):
        if not st.session_state.jobs:
            st.error("Fetch jobs first.")
        else:
            st.session_state.index = build_index(st.session_state.jobs)
            st.success("Index built.")

    if st.button("3) Find Top Matches"):
        if st.session_state.index is None:
            st.error("Build index first.")
        else:
            results = rank_jobs(st.session_state.index, profile, preferences, top_n=5)
            st.subheader("Match results (raw JSON per job)")
            for r in results[:10]:
                st.markdown(f"### Job ID: {r['job_id']}")
                st.code(r["raw"], language="json")
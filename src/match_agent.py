from typing import Dict, Any, List
import time
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

def _llm():
    # Set via OPENAI_API_KEY env var
    Settings.llm = OpenAI(model="gpt-4o-mini")
    return Settings.llm

def rank_jobs(index: VectorStoreIndex, profile_text: str, preferences_text: str, top_n: int = 5) -> List[Dict[str, Any]]:
    llm = _llm()
    retriever = index.as_retriever(similarity_top_k=max(top_n * 3, 12))

    # Step 1: Build retrieval query from profile + prefs
    query = f"""
You are matching job postings to a candidate.
Candidate profile:
{profile_text}

Preferences:
{preferences_text}

Retrieve the most relevant job requirements and responsibilities to evaluate fit.
""".strip()

    nodes = retriever.retrieve(query)

    # Group nodes by job_id
    by_job: Dict[str, List] = {}
    for n in nodes:
        jid = n.metadata.get("job_id")
        by_job.setdefault(jid, []).append(n)

    # Step 2: Ask LLM to score each job using evidence chunks
    results = []
    for jid, chunks in by_job.items():
        evidence = "\n\n".join(
            [f"[chunk {i+1}] {c.get_content()}\nMETA: {c.metadata}" for i, c in enumerate(chunks[:6])]
        )

        prompt = f"""
Return ONLY valid JSON.

Task: Score job fit from 0-100 for the candidate. Use ONLY the evidence provided.
Include:
- score (0-100)
- reasons: 3-6 bullets, each must quote or paraphrase a requirement and cite chunk numbers like ["chunk 1","chunk 3"]
- gaps: 1-5 bullets (what candidate seems missing)
- pitch_paragraph: 4-6 sentences
- job: title, company, location, url (from metadata in evidence)

Candidate profile:
{profile_text}

Preferences:
{preferences_text}

Evidence:
{evidence}
""".strip()

        # Small retry/backoff for transient 429s
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                resp = llm.chat([ChatMessage(role="user", content=prompt)])
                results.append({"job_id": jid, "raw": resp.message.content})
                break
            except Exception as e:
                if attempt == max_attempts:
                    results.append({"job_id": jid, "raw": '{"error": "rate limit or API error"}'})
                else:
                    time.sleep(2 ** attempt)

    # Step 3: Basic ranking heuristic: parse JSON later in UI; for MVP, just return raw
    return results
# Job Match Agent

An AI-powered job matching system that uses RAG (Retrieval-Augmented Generation) and semantic search to match job postings to candidates.

## Features

- **Multi-ATS Support**: Fetch jobs from Lever and Greenhouse job boards
- **Vector Search**: Semantic search using HuggingFace embeddings (free, no OpenAI charges for indexing)
- **AI Matching**: GPT-4o-mini scores job fit with detailed reasons, skill gaps, and pitch paragraphs
- **Streamlit UI**: Interactive web app for fetching, indexing, and ranking jobs
- **Cost-Optimized**: Uses free embeddings + minimal LLM calls (configurable `top_n`)

## Architecture

```
app.py                          # Streamlit UI
├── src/
│   ├── models.py              # JobPosting data model (Pydantic)
│   ├── normalize.py           # URL routing to fetchers
│   ├── index_store.py         # Vector indexing with Chroma + HuggingFace embeddings
│   ├── match_agent.py         # LLM ranking agent (GPT-4o-mini)
│   └── fetchers/
│       ├── lever.py           # Lever API integration
│       ├── greenhouse.py      # Greenhouse API integration (stub)
│       └── test.py            # Test utilities
```

## Setup

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install "numpy<2"  # Fix NumPy ABI compatibility
```

### 3. Set OpenAI API Key
Create a `.env` file in the project root:
```bash
echo 'export OPENAI_API_KEY="sk-..."' > .env
source .env
```

Or set directly in terminal:
```bash
export OPENAI_API_KEY="sk-..."
```

### 4. Run the App
```bash
streamlit run app.py
```

Visit `http://localhost:8501`

## Usage

### Step 1: Fetch Jobs
1. Paste ATS board URLs (one per line):
   - `https://jobs.lever.co/<company>` (Lever)
   - `https://api.lever.co/v0/postings/<company>` (Lever API)
2. Click **"1) Fetch Jobs"**
3. Preview fetched postings

### Step 2: Build Index
- Click **"2) Build Index"** to create semantic search index
- Uses free HuggingFace embeddings (BAAI/bge-small-en-v1.5)
- No OpenAI charges for this step

### Step 3: Find Top Matches
1. Fill in your **profile/resume text** and **preferences**
2. Click **"3) Find Top Matches"**
3. View scored jobs with:
   - Fit score (0-100)
   - 3-6 reasons (with chunk citations)
   - Skill gaps
   - Pitch paragraph
   - Job details (title, company, location, URL)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | For LLM ranking (gpt-4o-mini) |

## Cost Estimation

- **Index Building**: Free (HuggingFace embeddings)
- **Job Matching**: ~$0.0005 per job × `top_n` (default 5 jobs = ~$0.0025 per run)

Adjust `top_n=3` in [app.py](app.py) to reduce costs further.

## Key Components

### `JobPosting` (models.py)
Pydantic model for structured job data:
```python
class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str]
    description: str
    url: str
    remote: Optional[bool]
    posted_date: Optional[str]
    source: str  # "lever" | "greenhouse"
```

### `build_index()` (index_store.py)
- Converts jobs to Documents
- Creates Chroma vector store
- Uses HuggingFace embeddings for semantic search

### `rank_jobs()` (match_agent.py)
- Retrieves top-k most relevant jobs via semantic search
- Scores each job with GPT-4o-mini
- Includes retry/backoff for rate limits
- Returns structured JSON results

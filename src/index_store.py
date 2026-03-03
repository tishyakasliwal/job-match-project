from typing import List, Tuple
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from .models import JobPosting
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

def build_index(jobs: List[JobPosting]) -> VectorStoreIndex:
    documents: List[Document] = []
    for j in jobs:
        documents.append(Document(
            text=j.description,
            metadata={
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location or "",
                "url": j.url,
                "remote": j.remote,
                "posted_date": j.posted_date,
                "details": j.details or "",
                "source": j.source,
            }
        ))

    client = chromadb.EphemeralClient()  # in-memory for MVP
    collection = client.get_or_create_collection("jobs")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Use free HuggingFace embeddings instead of OpenAI
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.embed_model = embed_model

    return VectorStoreIndex.from_documents(documents, storage_context=storage_context)
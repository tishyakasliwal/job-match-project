from typing import List, Tuple
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from .models import JobPosting
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

def build_index(jobs: List[JobPosting]) -> VectorStoreIndex:
    """
    Build a semantic search index from job postings.
    
    Args:
        jobs: List of JobPosting objects to index
        
    Returns:
        VectorStoreIndex: A searchable vector index backed by Chroma
        
    Process:
        1. Convert each job to a Document with description as searchable text
        2. Store job metadata (title, company, location, etc.) for retrieval
        3. Initialize Chroma in-memory vector store
        4. Use free HuggingFace embeddings (BAAI/bge-small-en-v1.5) to embed job descriptions
        5. Return index ready for semantic search
    """
    documents: List[Document] = []
    # Step 1: Convert JobPostings to LlamaIndex Documents
    # Only description is embedded for semantic search; metadata is stored for retrieval
    for j in jobs:
        documents.append(Document(
            text=j.description,
            metadata={
                # Metadata stored but NOT embedded; used for filtering & display
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

    # Step 2: Initialize vector store (Chroma) for in-memory MVP
    client = chromadb.EphemeralClient()  # in-memory for MVP
    collection = client.get_or_create_collection("jobs")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Step 3: Configure embeddings (free HuggingFace instead of paid OpenAI)
    # Use free HuggingFace embeddings instead of OpenAI
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.embed_model = embed_model

    # Step 4: Build the index (embeds all documents and stores in Chroma)
    return VectorStoreIndex.from_documents(documents, storage_context=storage_context)
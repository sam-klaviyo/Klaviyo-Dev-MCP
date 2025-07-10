from sentence_transformers import SentenceTransformer
import numpy as np
import time
import os
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext, load_index_from_storage
import faiss

embed_model = HuggingFaceEmbedding(model_name="avsolatorio/GIST-small-Embedding-v0")
Settings.embed_model = embed_model
Settings.llm = None

def test_faiss_index():
    """Simple test to create FAISS index with test strings"""
    # Test strings
    test_strings = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language for data science",
        "Natural language processing helps computers understand human language",
        "Deep learning uses neural networks with multiple layers"
    ]
    
    print("Creating documents from test strings...")
    documents = [Document(text=text) for text in test_strings]
    
    # Initialize embedding model
    print("Loading embedding model: avsolatorio/GIST-small-Embedding-v0")
    
    # Create FAISS vector store
    print("Creating FAISS vector store...")
    dimension = 384  # GIST-small-Embedding-v0 dimension
    faiss_index = faiss.IndexFlatL2(dimension)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    
    # Create vector store index
    print("Building vector store index...")
    start = time.time()
    index = VectorStoreIndex.from_documents(
        documents, 
        vector_store=vector_store,
        embed_model=embed_model
    )
    end = time.time()
    print(f"Index creation time: {end - start} seconds")
    
    # Test query
    print("\nTesting query...")
    retriever = index.as_retriever()
    query = "What is machine learning?"
    response = retriever.retrieve(query)
    print(f"Query: {query}")
    print(f"Response: {response}")
    
    return index

def create_and_store_index():
    """Create index with test strings and store to local directory"""
    # Test strings
    test_strings = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language for data science",
        "Natural language processing helps computers understand human language",
        "Deep learning uses neural networks with multiple layers"
    ]
    
    print("Creating documents from test strings...")
    documents = [Document(text=text) for text in test_strings]
    
    # Initialize embedding model
    print("Loading embedding model: avsolatorio/GIST-small-Embedding-v0")
    embed_model = HuggingFaceEmbedding(model_name="avsolatorio/GIST-small-Embedding-v0")
    Settings.embed_model = embed_model
    Settings.llm = None
    
    # Create FAISS vector store
    print("Creating FAISS vector store...")
    dimension = 384  # GIST-small-Embedding-v0 dimension
    faiss_index = faiss.IndexFlatL2(dimension)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    storage_context.llm = None
    storage_context.embed_model = embed_model
    
    # Create vector store index
    print("Building vector store index...")
    start = time.time()
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        embed_model=embed_model
    )
    end = time.time()
    print(f"Index creation time: {end - start} seconds")
    
    # Create index directory if it doesn't exist
    os.makedirs("index", exist_ok=True)
    
    # Store index - save FAISS index separately
    print("Storing index to local directory...")
    index.storage_context.persist(persist_dir="index")
    
    return index

def load_and_query_index(dir_path: str):
    """Load index from local directory and perform retrieval"""
    # Load embedding model
    print("Loading embedding model: avsolatorio/GIST-small-Embedding-v0")
    embed_model = HuggingFaceEmbedding(model_name="avsolatorio/GIST-small-Embedding-v0")
    
    # Load FAISS index
    vector_store = FaissVectorStore.from_persist_dir(dir_path)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=dir_path
    )
    index = load_index_from_storage(storage_context=storage_context)
    
    # Get input query
    query = input("Enter your query: ")
    
    # Perform retrieval
    print("Performing retrieval...")
    retriever = index.as_retriever(similarity_top_k=5)
    response = retriever.retrieve(query)
    
    print(f"\nQuery: {query}")
    print(f"Retrieved documents:")
    for i, doc in enumerate(response):
        print(f"{i+1}. {doc.text}")
        print("-"*100)
    
    return response

if __name__ == "__main__":
    print("Starting FAISS index test...")
    print(f"Process ID: {os.getpid()}")
    # create_and_store_index()
    load_and_query_index("./index")

from llama_index.core import Document
from llama_index.core.node_parser import SimpleFileNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import faiss
import os
import re
from typing import List

from test_index import load_and_query_index


embed_model = HuggingFaceEmbedding(model_name="avsolatorio/GIST-small-Embedding-v0")
Settings.embed_model = embed_model
Settings.llm = None

def create_faiss_index():
    dimension = 384  # GIST-small-Embedding-v0 dimension
    faiss_index = faiss.IndexFlatL2(dimension)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    return vector_store

def split_documents(documents: list[Document], chunk_size: int = 3, max_chunk_length: int = 2000):
    """
    Split documents into smaller chunks based on sentences.
    
    Args:
        documents: List of Document objects to split
        chunk_size: Number of sentences per chunk (default: 3)
        max_chunk_length: Maximum character length per chunk (default: 2000)
    
    Returns:
        List of Document objects with sentence-based chunks
    """
    # Robust regex pattern for sentence splitting
    # Handles various sentence endings: ., !, ?, and accounts for abbreviations
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    
    result_documents = []
    
    for doc in documents:
        text = doc.text
        metadata = doc.metadata.copy()  # Preserve original metadata
        
        # Split text into sentences using regex
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences (remove empty ones, strip whitespace)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Create chunks based on chunk_size
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed max_chunk_length
            if current_length + sentence_length > max_chunk_length and current_chunk:
                # Finalize current chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_length += sentence_length
                
                # Check if we've reached chunk_size
                if len(current_chunk) >= chunk_size:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0
        
        # Add any remaining sentences as the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Create new Document objects for each chunk
        for i, chunk_text in enumerate(chunks):
            # Add chunk information to metadata
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            chunk_metadata['chunk_size'] = chunk_size
            
            # Create new Document with chunked text and preserved metadata
            chunk_doc = Document(
                text=chunk_text,
                metadata=chunk_metadata
            )
            result_documents.append(chunk_doc)
    
    return result_documents

def test_ingestion(input_path: str, dir_path: str):
    # Create directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    
    # Load FAISS index
    vector_store = create_faiss_index()

    reader = SimpleDirectoryReader(input_dir=input_path, recursive=True)

    # Ingest documents directly into faiss storage
    documents = reader.load_data(num_workers=4) 
    print(f"Loaded {len(documents)} documents")
    print(f"Original document text: {documents[0].text[:200]}...")
    print(f"Document metadata: {documents[0].metadata}")

    # Split documents into sentence-based chunks
    chunked_documents = split_documents(documents, chunk_size=3, max_chunk_length=2000)
    print(f"Created {len(chunked_documents)} chunked documents")
    print(f"Sample chunked document: {chunked_documents[0].text[:200]}...")
    print(f"Chunk metadata: {chunked_documents[0].metadata}")

    # Create storage context with the vector store and embed model (like test_index.py)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    storage_context.llm = None
    storage_context.embed_model = embed_model
    
    # Create index from chunked documents with proper storage context
    index = VectorStoreIndex.from_documents(
        chunked_documents, 
        storage_context=storage_context,
        embed_model=embed_model
    )

    retriever = index.as_retriever()
    response = retriever.retrieve("What is the reporting consistency policy?")
    print(f"Response: {response}")

    # Store the index using the same pattern as test_index.py
    index.storage_context.persist(persist_dir=dir_path)

if __name__ == "__main__":
    # test_ingestion("/Users/sam.onuallain/Klaviyo/Repos/eng-handbook/_team_docs", "./test_index")
    load_and_query_index("./test_index")
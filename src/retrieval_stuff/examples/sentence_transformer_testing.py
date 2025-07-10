from sentence_transformers import SentenceTransformer
import numpy as np
import time
import os

# Model takes up around 1.3GB of memory
def test_embedding():
    """Simple test function to embed text using the specified model"""
    # Load the model
    print("Loading model: avsolatorio/GIST-small-Embedding-v0")
    model = SentenceTransformer('avsolatorio/GIST-small-Embedding-v0')
    
    # Get input from user
    text = input("Enter text to embed: ")
    
    # Generate embedding
    print("Generating embedding...")
    start = time.time()
    embedding = model.encode(text)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    
    # Display results
    print(f"\nInput text: {text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 10 values): {embedding[:10]}")
    print(f"Embedding (last 10 values): {embedding[-10:]}")
    
    return embedding

if __name__ == "__main__":
    print("Starting test...")
    print(f"Process ID: {os.getpid()}")
    test_embedding()

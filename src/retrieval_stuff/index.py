from llama_index.core import Settings, Document, VectorStoreIndex, load_index_from_storage, StorageContext, ServiceContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss
import os

class Index:
    def __init__(self, index_name: str, path: str, chunk_size: int = 5_000):
        raise NotImplementedError("Subclasses must implement this method")

    def create(self, documents: list[Document]):
        # Create a new index for the first time.
        raise NotImplementedError("Subclasses must implement this method")
    
    def store(self):
        # Store the index in the database.
        raise NotImplementedError("Subclasses must implement this method")
    
    def update(self, documents: list[Document]):
        # Update the index with new documents.
        raise NotImplementedError("Subclasses must implement this method")
    
    def load(self, override: bool = False):
        # Load the index from the database.
        if not self.index or override:
            try:
                self._load_index()
            except Exception as e:
                print(f"Error loading index {self.index_name}: {e}")
        else:
            print("Index already loaded. Use override=True to load a new index.")
            return
        

    def _load_index(self, override: bool = False):
        raise NotImplementedError("Subclasses must implement this method")



class HuggingFaceVectorStoreIndex(Index):
    def __init__(self, index_name: str,
                 path: str, 
                 chunk_size: int = 5_000,
                 hf_name: str = "avsolatorio/GIST-small-Embedding-v0", 
                 dimension: int = 384):
        
        self.index_name = index_name
        self.path = path
        self.index = None
        self._setup_storage_context(hf_name, dimension, chunk_size)




    def _setup_storage_context(self, hf_name: str, dimension: int, chunk_size: int):
        embed_model = HuggingFaceEmbedding(model_name=hf_name)
        
        # Set LlamaIndex settings
        Settings.embed_model = embed_model
        Settings.llm = None
        Settings.chunk_size = chunk_size
        
        # Create storage context
        faiss_index = faiss.IndexFlatL2(dimension)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        self.storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.storage_context.llm = None
        self.storage_context.embed_model = embed_model
        self.storage_context.chunk_size = chunk_size
    
    
    
    def create(self, documents: list[Document]):
        """
        Create a new index for the first time.
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        print(f"Creating index {self.index_name}...")
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=self.storage_context,
            embed_model=self.storage_context.embed_model
        )
        print(f"Index {self.index_name} created.")
        self.index = index
    
    
    def store(self):
        """
        Store the index in the database.
        """
        print(f"Storing index {self.index_name}...")
        if self.index is not None:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            self.index.storage_context.persist(persist_dir=self.path)
            print(f"Index {self.index_name} stored.")
        else:
            raise ValueError("Index is not created yet. Please load the index first.")

    
    
    def update(self, documents: list[Document]):
        """
        Update the index with new documents.
        """
        if self.index is not None:
            self.index.update(documents)
        else:
            raise ValueError("Index is not created yet. Please load the index first.")

    
    
    def _load_index(self):
        print(f"Loading index {self.index_name}...")
        vector_store = FaissVectorStore.from_persist_dir(self.path)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=self.path
        )
        self.storage_context = storage_context
        self.index = load_index_from_storage(storage_context=storage_context)
        print(f"Index {self.index_name} loaded.")



if __name__ == "__main__":
    index = HuggingFaceVectorStoreIndex(
        index_name="test",
        path="./test_index"
    )
    
    index.create([Document(text="Hello, world!")])
    index.store()
    
    
    # index.load()
    # print(index.index.as_retriever().retrieve("Hello, world!"))
            
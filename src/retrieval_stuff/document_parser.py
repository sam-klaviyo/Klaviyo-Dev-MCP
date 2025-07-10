from llama_index.core import Document, SimpleDirectoryReader
import re
import os
import json
from tqdm import tqdm


def chunk_document(doc: Document, char_limit: int, sentence_num: int) -> list[Document]:
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    result_documents = []

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
        if current_length + sentence_length > char_limit and current_chunk:
            # Finalize current chunk
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_length += sentence_length
            
            # Check if we've reached chunk_size
            if len(current_chunk) >= sentence_num:
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
        chunk_metadata['chunk_size'] = sentence_num
        
        # Create new Document with chunked text and preserved metadata
        chunk_doc = Document(
            text=chunk_text,
            metadata=chunk_metadata
        )
        result_documents.append(chunk_doc)


    return result_documents

class DocumentParser:
    """
    Standard interface for parsing dociuments and exposing them to the indexer.
    """
    def __init__(self, dir_path: str, chunk_size: int):
        raise NotImplementedError("Subclasses must implement this method")

    
    
    def read_documents(self) -> list[any]:
        """
        Read documents from a directory and return a list of documents.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    
    def get_documents(self) -> list[Document]:
        """
        Get a list of documents from a directory given instance settings.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    
    
    def parse_document(self, document: any) -> Document:
        """
        Parse a single document of some type and return a Document object.
        """
        raise NotImplementedError("Subclasses must implement this method")

    
    
    def chunk_document(self, document: Document) -> list[Document]:
        """
        Chunk a document into a list of documents.
        """
        raise NotImplementedError("Subclasses must implement this method")



class EngHandbookDocumentParser(DocumentParser):
    def __init__(self, dir_path: str, sentence_num: int, chunk_size: int):
        self.dir_path = dir_path
        self.sentence_num = sentence_num
        self.chunk_size = chunk_size
    
    def read_documents(self) -> list[dict]:
        reader = SimpleDirectoryReader(input_dir=self.dir_path, recursive=True)
        documents = reader.load_data()
        return documents
    
    def get_documents(self) -> list[Document]:
        print(f"Getting documents from {self.dir_path}...")
        documents = self.read_documents()
        print(f"Found {len(documents)} documents.")
        
        print(f"Chunking {len(documents)} documents...")
        chunked_documents = []
        for doc in tqdm(documents):
            chunked_documents.extend(self.chunk_document(doc))
        print(f"Chunked {len(chunked_documents)} documents.")
        
        return chunked_documents
    
    
    def chunk_document(self, document: Document) -> list[Document]:
        return chunk_document(document, self.chunk_size, self.sentence_num)
        



class ConfluenceDocumentParser(DocumentParser):
    def __init__(self, dir_path: str, sentence_num: int = 8, chunk_size: int = 5_000):
        """
        Initialize the document parser.

        Args:
            dir_path: The path to the directory containing the documents.
            sentence_num: The number of sentences to include in each chunk.
            chunk_size: The maximum number of characters to include in each chunk.
        """
        
        self.dir_path = dir_path
        self.sentence_num = sentence_num
        self.chunk_size = chunk_size


    def read_documents(self) -> list[dict]:
        json_documents = []

        for root, _, files in os.walk(self.dir_path):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        json_documents.append(json.load(f))
        
        return json_documents
    
    
    
    def get_documents(self) -> list[Document]:
        """
        Retrieve json files from the directory recursively and parse them into Document objects.

        Returns:
            A list of Document objects, each containing a chunk of the original document.
        """

        # Get all json files in the directory recursively
        print(f"Getting documents from {self.dir_path}...")
        json_documents = self.read_documents()
        print(f"Found {len(json_documents)} documents.")

        print(f"Parsing {len(json_documents)} documents...")
        documents = [self.parse_document(doc) for doc in tqdm(json_documents)]
        print(f"Parsed {len(documents)} documents.")
        
        print(f"Chunking {len(documents)} documents...")
        chunked_documents = []
        for doc in tqdm(documents):
            chunked_documents.extend(self.chunk_document(doc))
        print(f"Chunked {len(chunked_documents)} documents.")
        
        return chunked_documents



   
   
    def parse_document(self, document: dict) -> Document:
        """
        Confluence documents are stored as JSON files in the directory. Turn them into a Document object.
        """
        doc = Document(text=document["clean_text"])
        doc.metadata = {
            "title": document["title"],
            "word_count": document["word_count"]
        }
        return doc

   
   
    def chunk_document(self, doc: Document) -> list[Document]:
        """
        Split documents into smaller chunks based on sentences. Limit chunks to a character limit.

        Returns:
            A list of Document objects, each containing a chunk of the original document.
        """

        # Robust regex pattern for sentence splitting
        # Handles various sentence endings: ., !, ?, and accounts for abbreviations
        return chunk_document(doc, self.chunk_size, self.sentence_num)
        
    
if __name__ == "__main__":
    # parser = ConfluenceDocumentParser(
    #     dir_path="confluence_pages",
    #     sentence_num=10,
    #     chunk_size=10_000
    # )

    parser = EngHandbookDocumentParser(
        dir_path="/Users/sam.onuallain/Klaviyo/Repos/eng-handbook",
        sentence_num=10,
        chunk_size=5_000
    )

    documents = parser.get_documents()
    print(f"Got {len(documents)} documents.")
    print("-"*100)
    print("EXAMPLE DOCUMENT:")
    print(documents[0].text)
    print(documents[0].metadata)
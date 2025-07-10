from document_parser import ConfluenceDocumentParser, EngHandbookDocumentParser
from index import HuggingFaceVectorStoreIndex
from retriever import HuggingFaceVectorRetriever

def confluence_example():
    chunk_size = 1024
    
    # parser = ConfluenceDocumentParser(
    #     dir_path="confluence_pages",
    #     sentence_num=5,
    #     char_limit=chunk_size
    # )
    # documents = parser.get_documents()
    
    confluence_index = HuggingFaceVectorStoreIndex(
        index_name="confluence_pages",
        path="./confluence_pages_index",
        chunk_size=chunk_size,
        hf_name="avsolatorio/GIST-small-Embedding-v0",
        dimension=384
    )
    # confluence_index.create(documents)
    # confluence_index.store()
    confluence_index.load()
    
    confluence_retriever = HuggingFaceVectorRetriever(confluence_index, top_k=10)
    retrieved_docs = confluence_retriever.retrieve("Who is the manager for the consistencty reporting team?", top_k=2)
    print("\n-----------\n".join(retrieved_docs))

def eng_handbook_example():
    chunk_size = 1024
    # parser = EngHandbookDocumentParser(
    #     dir_path="/Users/sam.onuallain/Klaviyo/Repos/eng-handbook",
    #     sentence_num=10,
    #     chunk_size=chunk_size
    # )
    # documents = parser.get_documents()

    eng_handbook_index = HuggingFaceVectorStoreIndex(
        index_name="eng_handbook",
        path="./eng_handbook_index",
        chunk_size=chunk_size,
        hf_name="avsolatorio/GIST-small-Embedding-v0",
        dimension=384
    )

    # eng_handbook_index.create(documents)
    # eng_handbook_index.store()
    eng_handbook_index.load()

    eng_handbook_retriever = HuggingFaceVectorRetriever(eng_handbook_index, top_k=10)
    retrieved_docs = eng_handbook_retriever.retrieve("What is the purpose of the Kvyo platform?", top_k=2)
    print("\n-----------\n".join(retrieved_docs))


if __name__ == "__main__":
    # confluence_example()
    eng_handbook_example()
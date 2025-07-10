from index import HuggingFaceVectorStoreIndex, Index
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import BaseRetriever



class Retriever:
    def __init__(self, index: Index, top_k: int = 10):
        raise NotImplementedError("Subclasses must implement this method")
    
    def retrieve(self, query: str, rerank: bool = False, top_k: int = None) -> list[str]:
        raise NotImplementedError("Subclasses must implement this method")
    
    def build_retriever(self) -> BaseRetriever:
        raise NotImplementedError("Subclasses must implement this method")
    
    def rerank(self, retrieved_nodes: list[NodeWithScore]) -> list[str]:
        raise NotImplementedError("Subclasses must implement this method")
    

# TODO: maybe make a hybrid one?
class HuggingFaceVectorRetriever(Retriever):
    def __init__(self, index: HuggingFaceVectorStoreIndex, top_k: int = 10):
        assert isinstance(index, HuggingFaceVectorStoreIndex), "Index must be a HuggingFaceVectorStoreIndex"
        
        self.index = index
        self.top_k = top_k
        self.retriever = self.build_retriever()

    def retrieve(self, query: str, rerank: bool = False, top_k: int = None) -> list[str]:
        print(f"Retrieving {self.top_k} documents for query: '{query}'...")
        retrieved_nodes = self.retriever.retrieve(query)
        print(f"Retrieved {len(retrieved_nodes)} documents.")
        if rerank:
            retrieved_nodes = self.rerank(retrieved_nodes)
            print(f"Reranked {len(retrieved_nodes)} documents.")
        if top_k is not None:
            retrieved_nodes = retrieved_nodes[: top_k]
        
        return self._parse_results(retrieved_nodes)
    
    def _parse_results(self, retrieved_nodes: list[NodeWithScore]) -> list[str]:
        results = []
        for node in retrieved_nodes:
            doc = "File Path: {}\n -----------\n Title: {}\n -----------\n Content: {}"
            doc = doc.format(
                node.node.metadata.get("file_path", "Unknown"), 
                node.node.metadata.get("title", "Unknown"), 
                node.node.text)
            results.append(doc)
        return results


    def build_retriever(self) -> BaseRetriever:
        return self.index.index.as_retriever(similarity_top_k=self.top_k)

    def rerank(self, retrieved_nodes: list[NodeWithScore]) -> list[str]:
        return retrieved_nodes



if __name__ == "__main__":
    # Load index
    index = HuggingFaceVectorStoreIndex(
        index_name="test",
        path="./test_index"
    )
    index.load()

    retriever = HuggingFaceVectorRetriever(index, top_k=10)
    print(retriever.retrieve("Hello, world!"))
        
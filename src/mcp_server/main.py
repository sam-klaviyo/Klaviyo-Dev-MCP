from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import mcp.types as types
import argparse

from src.retrieval_stuff.index import HuggingFaceVectorStoreIndex
from src.retrieval_stuff.retriever import HuggingFaceVectorRetriever

confluence_index = None
confluence_retriever = None
guidebook_index = None
guidebook_retriever = None

# Initialize FastMCP server
mcp = FastMCP(
    "Klaviyo Dev MCP",
    instructions="""This server provides access to Klaviyo's engineering documentation and resources.
                    It is designed to help developers and engineers find information about Klaviyo's products,
                    processes, and best practices.
                    It has access to Klaviyo's confluence knowledge base, and its engineering guidebook which has information about common engineering tasks and processes.""")

@mcp.tool()
def search_confluence(query: str) -> str:
    """Search Klaviyo's confluence knowledge base for information."""
    return "\n".join(confluence_retriever.retrieve(query))

@mcp.tool()
def search_engineering_guidebook(query: str) -> str:
    """Search Klaviyo's engineering guidebook for information."""
    return "\n".join(guidebook_retriever.retrieve(query))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confluence", action="store_true", help="Use confluence as a knowledge base")
    parser.add_argument("--confluence_path", type=str, default="index/confluence_pages_index", help="Path to the confluence index")
    parser.add_argument("--guidebook", action="store_true", help="Use the engineering guidebook as a knowledge base")
    parser.add_argument("--guidebook_path", type=str, default="index/eng_handbook_index", help="Path to the guidebook index")
    parser.add_argument("--top_k", type=int, default=10, help="Number of results to return")
    args = parser.parse_args()

    if args.confluence:
        print("Loading confluence index...")
        confluence_index = HuggingFaceVectorStoreIndex(
            index_name="confluence_pages_index",
            path=args.confluence_path
        )
        confluence_index.load()
        confluence_retriever = HuggingFaceVectorRetriever(confluence_index, top_k=args.top_k)

    if args.guidebook:
        print("Loading guidebook index...")
        guidebook_index = HuggingFaceVectorStoreIndex(
            index_name="eng_handbook_index",
            path=args.guidebook_path
        )
        guidebook_index.load()
        guidebook_retriever = HuggingFaceVectorRetriever(guidebook_index, top_k=args.top_k)
    
    print("Starting MCP server...")
    mcp.run(transport='stdio')
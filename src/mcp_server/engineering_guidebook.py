from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# Initialize FastMCP server
mcp = FastMCP(
    "engineering_guidebook",
    instructions="""This server is used to search Klaviyo's engineering guidebook for information. It uses the complex_query tool to break down the query into sub-queries and the search_two tool to perform the actual search.
                    The engineering guidebook has information about Klaviyo's engineering processes and details that are not publicly available.
                    The engineering guidebook is stored in a knowledge base and is updated regularly.""")

@mcp.tool()
async def complex_query(query: str) -> str:
    """
    Break down a complex query into sub-queries using the search_complex_query prompt.
    This tool gives you a prompt specifiying how to break down the query into sub-queries.
    After generating the sub-queries, you will need to call search_two for each sub-query to perform the actual search.
    """

    return f""""You are an expert query analyst. Your task is to take a user's original query and break it down into a series of concise and specific sub-queries. These sub-queries will be used to retrieve relevant information from a knowledge base.

                  Your process should be as follows:
                  1.  **Analyze the original query:** Identify the distinct questions, entities, and concepts within the user's request.
                  2.  **Decompose into sub-queries:** Generate a numbered list of atomic sub-queries. Each sub-query should be a direct question that can be answered independently.
                  3.  **Handle simplicity:** If the original query is already simple and cannot be broken down further, return the original query as the only item in the list.

                  **Example 1: Complex Query**
                  **Original Query:** 'What were the economic impacts of the 2008 financial crisis on the US housing market, and how did the government's response, like TARP, affect this?'

                  **Decomposed Sub-Queries:**
                  1. What was the 2008 financial crisis?
                  2. How did the 2008 financial crisis impact the US housing market?
                  3. What were the key economic effects of the 2008 financial crisis on US housing?

                  **Example 2: Simple Query**
                  **Original Query:** 'Who is the current CEO of Google?'

                  **Decomposed Sub-Queries:**
                  1. Who is the current CEO of Google?

                  Now, process the following user query:

                  **Original Query:** {query}"""
    
    
@mcp.tool()
async def search_two(sub_queries: str) -> str:
    """
    Search for a specific sub-query. Currently returns the input as a placeholder.
    This tool will be used to actually search the knowledge base for each sub-query.
    Input must be in list format separated by commas (e.g., "query1, query2, query3").
    """
    return f"Search result for: {sub_queries}\n\nThis is a placeholder response. The actual search implementation will be added here."

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport='stdio')
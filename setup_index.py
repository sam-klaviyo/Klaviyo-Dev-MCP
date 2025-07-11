#!/usr/bin/env python3
"""
Setup script for building Confluence and Engineering Handbook indexes.
This script provides a more maintainable and extensible alternative to the bash version.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from retrieval_stuff.confluence_scraper import ConfluenceScraper
from retrieval_stuff.document_parser import ConfluenceDocumentParser, EngHandbookDocumentParser
from retrieval_stuff.index import HuggingFaceVectorStoreIndex
import dotenv


class IndexBuilder:
    """Base class for building different types of indexes."""
    
    def __init__(self, chunk_size: int, embed_model: str, dimension: int):
        self.chunk_size = chunk_size
        self.embed_model = embed_model
        self.dimension = dimension
        
    def build(self, **kwargs):
        """Build the index. To be implemented by subclasses."""
        raise NotImplementedError


class ConfluenceIndexBuilder(IndexBuilder):
    """Builder for Confluence indexes."""
    
    def build(self, space_keys: List[str], env_path: str = ".env", 
              index_path: str = "./index/confluence_pages_index"):
        """Build Confluence index."""
        print(f"Building Confluence index with spaces: {space_keys}")
        
        # Load environment variables
        dotenv.load_dotenv(dotenv_path=env_path, override=True)
        
        # Use temporary directory for confluence pages that automatically cleans up
        with tempfile.TemporaryDirectory(prefix="confluence_pages_") as temp_dir:
            # Download pages to temporary directory
            scraper = ConfluenceScraper(dir_path=temp_dir, space_keys=space_keys)
            scraper.download_pages()
            
            # Parse documents
            parser = ConfluenceDocumentParser(
                dir_path=temp_dir,
                chunk_size=self.chunk_size
            )
            documents = parser.get_documents()
            
            # Create and store index
            index = HuggingFaceVectorStoreIndex(
                index_name="confluence_pages",
                path=index_path,
                chunk_size=self.chunk_size,
                hf_name=self.embed_model,
                dimension=self.dimension
            )
            index.create(documents)
            index.store()
            
        print("✓ Confluence index built successfully")


class HandbookIndexBuilder(IndexBuilder):
    """Builder for Engineering Handbook indexes."""
    
    def build(self, handbook_path: str, 
              index_path: str = "./index/eng_handbook_index"):
        """Build Engineering Handbook index."""
        print("Building Engineering Handbook index...")
        
        # Check if handbook path exists
        if not os.path.isdir(handbook_path):
            raise FileNotFoundError(f"Handbook path '{handbook_path}' does not exist.")
        
        # Parse documents
        parser = EngHandbookDocumentParser(
            dir_path=handbook_path,
            chunk_size=self.chunk_size
        )
        documents = parser.get_documents()
        
        # Create and store index
        index = HuggingFaceVectorStoreIndex(
            index_name="eng_handbook",
            path=index_path,
            chunk_size=self.chunk_size,
            hf_name=self.embed_model,
            dimension=self.dimension
        )
        index.create(documents)
        index.store()
        
        print("✓ Engineering Handbook index built successfully")


def setup_environment():
    """Setup environment similar to the bash script."""
    # Check if .env file exists
    if not os.path.exists(".env"):
        raise FileNotFoundError("Error: .env file not found. Please create .env file with required environment variables.")
    
    # Load environment variables
    dotenv.load_dotenv(dotenv_path=".env", override=True)
    
    # Set PYTHONPATH
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Create index directory
    os.makedirs("index", exist_ok=True)


def main():
    """Main function to parse arguments and build indexes."""
    parser = argparse.ArgumentParser(
        description="Setup script for building Confluence and Engineering Handbook indexes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --confluence ResDev EN
  %(prog)s --handbook
  %(prog)s --confluence --handbook ResDev EN DEVOPS
  %(prog)s --confluence --embed_model sentence-transformers/all-MiniLM-L6-v2 ResDev EN
        """
    )
    
    # Index type flags
    parser.add_argument(
        "--confluence", 
        action="store_true",
        help="Enable building confluence index"
    )
    parser.add_argument(
        "--handbook", 
        action="store_true",
        help="Enable building handbook index"
    )
    
    # Configuration arguments
    parser.add_argument(
        "--embed_model",
        type=str,
        default="avsolatorio/GIST-small-Embedding-v0",
        help="Embedding model to use (default: avsolatorio/GIST-small-Embedding-v0)"
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=2048,
        help="Size of the chunks (default: 2048)"
    )
    parser.add_argument(
        "--dimension",
        type=int,
        default=384,
        help="Dimension of the embedding model (default: 384)"
    )
    
    # Path arguments
    parser.add_argument(
        "--handbook_path",
        type=str,
        default="/Users/sam.onuallain/Klaviyo/Repos/eng-handbook",
        help="Path to the engineering handbook directory"
    )
    parser.add_argument(
        "--env_path",
        type=str,
        default=".env",
        help="Path to the .env file (default: .env)"
    )
    
    # Confluence space keys (remaining positional arguments)
    parser.add_argument(
        "space_keys",
        nargs="*",
        help="Confluence space keys (required if --confluence is used)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.confluence and not args.handbook:
        parser.error("At least one of --confluence or --handbook must be specified")
    
    if args.confluence and not args.space_keys:
        parser.error("Space keys are required when --confluence is used")
    
    print("Setting up indexes...")
    print(f"Confluence: {args.confluence}")
    print(f"Handbook: {args.handbook}")
    print(f"Embedding model: {args.embed_model}")
    print(f"Chunk size: {args.chunk_size}")
    
    if args.confluence:
        print(f"Space keys: {args.space_keys}")
    
    try:
        # Setup environment
        setup_environment()
        
        # Build indexes
        if args.confluence:
            builder = ConfluenceIndexBuilder(
                chunk_size=args.chunk_size,
                embed_model=args.embed_model,
                dimension=args.dimension
            )
            builder.build(
                space_keys=args.space_keys,
                env_path=args.env_path
            )
        
        if args.handbook:
            builder = HandbookIndexBuilder(
                chunk_size=args.chunk_size,
                embed_model=args.embed_model,
                dimension=args.dimension
            )
            builder.build(handbook_path=args.handbook_path)
        
        print("\nSetup completed successfully!\n")
        print("You can now run the MCP server with:")
        print("./run_mcp.sh")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
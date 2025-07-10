import argparse
from document_parser import ConfluenceDocumentParser
from src.retrieval_stuff.index import HuggingFaceVectorStoreIndex
from confluence_scraper import ConfluenceScraper
import tempfile
import dotenv

def main():
    """
    Example usage:
    python build_confluence_index.py --sentence_num 10 --chunk_size 1024 --hf_name "avsolatorio/GIST-small-Embedding-v0" --dimension 384 --index_path ./confluence_pages_index --confluence_spaces "ResDev" "EN" --env_path .env
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--sentence_num", type=int, required=True, help="Number of sentences per chunk")
    parser.add_argument("--chunk_size", type=int, required=True, help="Size of the chunks")
    parser.add_argument("--hf_name", type=str, required=True, help="Name of the huggingface model to use")
    parser.add_argument("--dimension", type=int, required=True, help="Dimension of the huggingface model")
    parser.add_argument("--index_path", default="./index/confluence_pages_index", type=str, required=False, help="Path to the index")
    parser.add_argument("--confluence_spaces", nargs="+", required=True, help="Spaces to scrape")
    parser.add_argument("--env_path", type=str, required=True, help="Path to the .env file")

    args = parser.parse_args()
    print("Downloading all pages from the following spaces:", args.confluence_spaces)

    dotenv.load_dotenv(dotenv_path=args.env_path, override=True)

    # Use temporary directory for confluence pages that automatically cleans up after index is created
    with tempfile.TemporaryDirectory(prefix="confluence_pages_") as temp_dir:
        # Download pages to temporary directory
        scraper = ConfluenceScraper(dir_path=temp_dir, space_keys=args.confluence_spaces)
        scraper.download_pages()
        
        # Parse documents
        parser = ConfluenceDocumentParser(
            dir_path=temp_dir,
            sentence_num=args.sentence_num,
            chunk_size=args.chunk_size
        )
        documents = parser.get_documents()

        # Create and store index
        index = HuggingFaceVectorStoreIndex(
            index_name="confluence_pages",
            path=args.index_path,
            chunk_size=args.chunk_size,
            hf_name=args.hf_name,
            dimension=args.dimension
        )
        index.create(documents)
        index.store()

if __name__ == "__main__":
    main()
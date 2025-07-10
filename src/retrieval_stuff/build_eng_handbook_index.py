import argparse
from document_parser import EngHandbookDocumentParser
from index import HuggingFaceVectorStoreIndex


def main():
    """
    Example usage:
    python src/retrieval_stuff/build_eng_handbook_index.py --handbook_path /Users/sam.onuallain/Klaviyo/Repos/eng-handbook --sentence_num 10 --chunk_size 1024 --hf_name "avsolatorio/GIST-small-Embedding-v0" --dimension 384
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--handbook_path", type=str, required=True)
    parser.add_argument("--sentence_num", type=int, required=True)
    parser.add_argument("--chunk_size", type=int, required=True)
    parser.add_argument("--hf_name", type=str, required=True)
    parser.add_argument("--dimension", type=int, required=True)
    parser.add_argument("--index_path", default="./index/eng_handbook_index", type=str, required=False)
    args = parser.parse_args()
    
    parser = EngHandbookDocumentParser(
        dir_path=args.handbook_path,
        sentence_num=args.sentence_num,
        chunk_size=args.chunk_size
    )
    documents = parser.get_documents()
    
    index = HuggingFaceVectorStoreIndex(
        index_name="eng_handbook",
        path=args.index_path,
        chunk_size=args.chunk_size,
        hf_name=args.hf_name,
        dimension=args.dimension
    )
    index.create(documents)
    index.store()


if __name__ == "__main__":
    main()
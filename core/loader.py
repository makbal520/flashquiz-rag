from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

def load_and_split(pdf_path: str, chunk_size: int = 600, chunk_overlap: int = 100):
    # Load PDF
    loader = PyPDFLoader(str(Path(pdf_path)))
    docs = loader.load()
    print(f"Pages loaded: {len(docs)}")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    return chunks
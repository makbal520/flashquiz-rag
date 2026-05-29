from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

CHROMA_PATH = "./chroma_db"

def get_vectorstore(chunks=None):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if not os.path.exists(CHROMA_PATH):
        print("Building vector store for the first time...")
        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=CHROMA_PATH
        )
        print("Vector store saved to disk")
    else:
        print("Loading existing vector store...")
        vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        print("Vector store loaded successfully")

    return vectorstore


def reset_vectorstore():
    import shutil
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
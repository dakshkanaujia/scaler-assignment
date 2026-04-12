import os
import httpx
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from typing import List

load_dotenv()

class GeminiEmbeddings(Embeddings):
    """Uses the Gemini v1beta REST API for embeddings."""
    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"

    def _embed(self, text: str) -> List[float]:
        r = httpx.post(
            self.url,
            params={"key": self.api_key},
            json={"model": f"models/{self.model}", "content": {"parts": [{"text": text}]}},
            timeout=30
        )
        r.raise_for_status()
        return r.json()["embedding"]["values"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


def ingest_data():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment.")
        return

    data_path = os.getenv("RESUME_TEXT_PATH", "./data/resume.txt")
    repos_path = os.getenv("GITHUB_REPOS_PATH", "./data/repos/")
    chroma_db_dir = "./chroma_db/"

    documents = []

    # Load resume
    if os.path.exists(data_path):
        if data_path.endswith(".txt"):
            loader = TextLoader(data_path)
            documents.extend(loader.load())
        elif data_path.endswith(".pdf"):
            loader = PyPDFLoader(data_path)
            documents.extend(loader.load())

    # Load git repos (recursively find .md files)
    if os.path.exists(repos_path):
        loader = DirectoryLoader(repos_path, glob="**/*.md", loader_cls=TextLoader)
        documents.extend(loader.load())

    if not documents:
        print("No documents found to ingest.")
        return

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    chunks = text_splitter.split_documents(documents)

    # Use native Gemini SDK embeddings (v1 API, not v1beta)
    embeddings = GeminiEmbeddings(api_key=api_key)

    # Persist vector store
    if os.path.exists(chroma_db_dir):
        import shutil
        shutil.rmtree(chroma_db_dir)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_db_dir
    )

    print(f"Ingested {len(chunks)} chunks from {len(documents)} documents.")
    print(f"Collection stored in {chroma_db_dir}")

if __name__ == "__main__":
    ingest_data()

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from agent.ingest import GeminiEmbeddings

load_dotenv()

def get_retriever():
    api_key = os.getenv("GEMINI_API_KEY")
    chroma_db_dir = "./chroma_db/"
    embeddings = GeminiEmbeddings(api_key=api_key)

    if not os.path.exists(chroma_db_dir):
        print("Chroma DB not found. Please run ingest.py first.")
        return None

    vectorstore = Chroma(
        persist_directory=chroma_db_dir,
        embedding_function=embeddings
    )
    return vectorstore.as_retriever(search_kwargs={"k": 3})

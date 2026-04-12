import os
import logging
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from agent.ingest import GeminiEmbeddings

load_dotenv()

logger = logging.getLogger(__name__)

def get_retriever():
    api_key = os.getenv("GEMINI_API_KEY")
    chroma_db_dir = "./chroma_db/"
    embeddings = GeminiEmbeddings(api_key=api_key)

    abs_path = os.path.abspath(chroma_db_dir)
    logger.info(f"Looking for chroma_db at: {abs_path} (exists={os.path.exists(chroma_db_dir)})")

    if not os.path.exists(chroma_db_dir):
        logger.warning(f"Chroma DB not found at {abs_path}. RAG will be unavailable.")
        return None

    vectorstore = Chroma(
        persist_directory=chroma_db_dir,
        embedding_function=embeddings
    )
    logger.info(f"Chroma DB loaded successfully from {abs_path}")
    return vectorstore.as_retriever(search_kwargs={"k": 6})

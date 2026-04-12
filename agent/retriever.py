import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

def get_retriever():
    chroma_db_dir = "./chroma_db/"
    embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001", task_type="retrieval_query")
    
    if not os.path.exists(chroma_db_dir):
        print("Chroma DB not found. Please run ingest.py first.")
        return None
        
    vectorstore = Chroma(
        persist_directory=chroma_db_dir,
        embedding_function=embeddings
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 4})

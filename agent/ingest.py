import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64
    )
    chunks = text_splitter.split_documents(documents)

    # Embeddings - Lightweight Gemini option
    embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001", task_type="retrieval_document", google_api_key=api_key)

    # Persist vector store
    # Idempotent: Overwrite existing collection
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

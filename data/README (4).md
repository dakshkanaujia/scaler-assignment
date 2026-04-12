# 🔍 Hybrid Retrieval System

A sophisticated information retrieval system that combines **vector search**, **graph-based exploration**, and **hybrid ranking** to deliver intelligent, context-aware search results. Built with a modern tech stack featuring FastAPI, Neo4j, FAISS, and React.

## 🎯 Project Overview

The Hybrid Retrieval System is an advanced search and knowledge discovery platform that leverages multiple retrieval strategies to provide superior search results. By combining dense vector embeddings, sparse BM25 retrieval, and graph-based knowledge relationships, the system can understand both semantic meaning and structural context.

## ✨ Key Features

### Search Capabilities
- **🔎 Vector Search**: Semantic search using FAISS for dense vector similarity
- **📊 Graph Search**: Explore knowledge through Neo4j graph relationships
- **🎯 Hybrid Search**: Combines vector and graph signals with configurable weights (α/β)
- **📝 BM25 Sparse Retrieval**: Traditional keyword-based search using BM25 algorithm
- **🔄 Reciprocal Rank Fusion (RRF)**: Intelligent merging of search results

### Data Management
- **📥 Document Ingestion**: NLP-powered text processing with entity extraction
- **🏷️ Entity Recognition**: Automatic extraction and linking of entities using SpaCy
- **🔗 Relationship Mapping**: Automatic creation of document-entity relationships
- **🗑️ CRUD Operations**: Full create, read, update, delete for nodes and edges

### Visualization
- **🌐 Interactive Graph**: Real-time force-directed graph visualization
- **🎨 Dynamic Highlighting**: Top search results highlighted in red
- **🖱️ Node Exploration**: Click to expand and explore graph neighborhoods
- **📱 Responsive UI**: Modern, dark-themed interface with glassmorphism

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Neo4j**: Graph database for relationships and traversals
- **FAISS (Facebook AI Similarity Search)**: Vector similarity search
- **Sentence Transformers**: Text embedding generation
- **SpaCy**: Natural language processing and entity recognition
- **BM25**: Sparse retrieval algorithm
- **NetworkX**: Graph algorithms and analysis

### Frontend
- **React 19**: Modern UI library
- **Vite**: Lightning-fast build tool
- **TailwindCSS 4**: Utility-first CSS framework
- **vis-network**: Interactive graph visualization
- **Axios**: HTTP client for API requests
- **Lucide React**: Beautiful icon library

## 📁 Project Structure

```
Hackathon/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── core/
│   │   │   └── config.py          # Configuration settings
│   │   ├── db/
│   │   │   ├── neo4j_client.py    # Neo4j connection
│   │   │   ├── faiss_client.py    # FAISS vector store
│   │   │   ├── bm25_client.py     # BM25 sparse retrieval
│   │   │   └── graph_store.py     # Graph operations
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── services/
│   │   │   ├── embedding.py       # Embedding generation
│   │   │   ├── ingestion.py       # Document processing
│   │   │   └── search.py          # Search algorithms
│   │   └── main.py                # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphVisualization.jsx
│   │   │   ├── IngestionModal.jsx
│   │   │   └── DebugPanel.jsx
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── App.jsx                # Main application
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚀 Setup Guide

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Neo4j**: 4.x or 5.x database instance
- **Git**: For version control

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download SpaCy language model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment variables** (create `.env` file):
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```

6. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

### Neo4j Setup

#### Option 1: Neo4j Desktop
1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new database
3. Set password and start the database
4. Note the Bolt URL (usually `bolt://localhost:7687`)

#### Option 2: Neo4j Docker
```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

#### Option 3: Neo4j Aura (Cloud)
1. Sign up at [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a free instance
3. Use the provided connection URI and credentials

## 💡 Usage

### 1. Ingest Documents

Click the **"Ingest Data"** button in the UI to add documents:
- Paste or type text content
- System automatically extracts entities and creates relationships
- Documents are indexed for vector and keyword search

### 2. Perform Searches

**Vector Search**:
- Select "Vector" tab
- Enter your query
- Returns semantically similar documents

**Hybrid Search** (Recommended):
- Select "Hybrid" tab
- Adjust α (vector weight) and β (graph weight) sliders
- Combines semantic similarity with graph connectivity
- Higher α emphasizes meaning, higher β emphasizes relationships

### 3. Explore the Graph

- Click on search result nodes to expand their neighborhoods
- View document details in the side panel
- Red nodes indicate top matches, green for other results
- Navigate through connected entities and documents

### 4. Manage Data

- Delete individual documents using the trash icon
- Reset entire database with "Reset Data" button
- Use Debug Panel (gear icon) for system insights

## 🔌 API Endpoints

### Ingestion
- `POST /api/ingest` - Ingest text and extract entities

### Search
- `POST /api/search/vector` - Vector similarity search
- `GET /api/search/graph` - Graph traversal search
- `POST /api/search/hybrid` - Hybrid search with configurable weights

### CRUD Operations
- `POST /api/nodes` - Create a new node
- `GET /api/nodes/{node_id}` - Get node details
- `PUT /api/nodes/{node_id}` - Update node
- `DELETE /api/nodes/{node_id}` - Delete node
- `POST /api/edges` - Create edge/relationship
- `GET /api/edges/{edge_id}` - Get edge details
- `PUT /api/edges/{edge_id}` - Update edge
- `DELETE /api/edges/{edge_id}` - Delete edge

### Utility
- `POST /api/reset` - Reset all data
- `DELETE /api/documents/{doc_id}` - Delete document

## 📊 Use Cases

### 1. **Knowledge Base Search**
Build an intelligent knowledge base where users can search through documentation, articles, and FAQs using natural language queries. The graph structure helps discover related content.

### 2. **Research Paper Discovery**
Index academic papers and leverage entity extraction to link papers through shared concepts, authors, and topics. Find papers not just by keywords but by conceptual similarity.

### 3. **Customer Support**
Create a support system that finds relevant solutions by understanding query intent and exploring related issues through the knowledge graph.

### 4. **Content Recommendation**
Recommend related articles, products, or content by combining semantic similarity with graph-based collaborative filtering.

### 5. **Legal Document Analysis**
Index legal documents, contracts, or case law. Find similar cases and explore legal precedents through citation graphs.

### 6. **Enterprise Search**
Build a company-wide search system that understands context and relationships between projects, people, and documents.

## 🎯 Outcome

This project demonstrates:
- **Hybrid Information Retrieval**: Combining multiple search paradigms for superior results
- **NLP Integration**: Automatic entity extraction and relationship mapping
- **Scalable Architecture**: Modular design supporting future enhancements
- **Modern UX**: Interactive, responsive interface with real-time feedback
- **Production-Ready APIs**: Well-structured REST endpoints with proper error handling

## 🔧 Development

### Running Tests
```bash
cd backend
pytest tests/
```

### Building for Production

**Backend**:
```bash
# Use production ASGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend**:
```bash
npm run build
npm run preview  # Preview production build
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Required |

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional search algorithms (e.g., dense passage retrieval)
- More sophisticated entity linking
- Multi-language support
- Advanced graph analytics
- Performance optimizations
- Enhanced visualization options

## 📄 License

This project was created as part of a hackathon demonstration.

## 🙏 Acknowledgments

Built with powerful open-source technologies:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Neo4j](https://neo4j.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [SpaCy](https://spacy.io/)
- [React](https://react.dev/)
- [TailwindCSS](https://tailwindcss.com/)
- [vis-network](https://visjs.org/)

---

**Built with ❤️ for intelligent information retrieval**

# AI Persona Code Agent

An AI representative built using Gemini 1.5 Pro, RAG context, and calendar management tools.

## Architecture

```
    +-----------------+        +---------------------+
    |  Streamlit UI    | <----> |  FastAPI Backend    |
    +-----------------+        +---------------------+
                                       |
                                       v
    +-----------------+        +---------------------+
    |   ChromaDB      | <----> |  Gemini 1.5 Agent   |
    |   (RAG Context) |        |  (Core Logic)       |
    +-----------------+        +---------------------+
                                       |
                                       v
                               +---------------------+
                               |  Calendar Tools     |
                               |  (Cal.com API)      |
                               +---------------------+
```

## Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd Scaler-Assignment
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables**:
    Copy `.env.example` to `.env` and fill in the required keys.
    ```bash
    cp .env.example .env
    ```

4.  **Ingest Data**:
    Place your resume in `./data/resume.txt` and repository files in `./data/repos/`. Run the ingestion script:
    ```bash
    python agent/ingest.py
    ```
    *Note: This project uses `GoogleGenerativeAIEmbeddings` for a lightweight local footprint.*

5.  **Run the application**:
    - Backend: `uvicorn api.main:app --reload`
    - Frontend: `streamlit run chat_ui/app.py`

## Environment Variables

| Variable | Description |
| --- | --- |
| `GEMINI_API_KEY` | Google AI Studio API Key |
| `CALCOM_API_KEY` | Cal.com API Key |
| `CALCOM_EVENT_TYPE_ID` | Cal.com Event Type ID |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (for future integrations) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (for future integrations) |
| `TWILIO_PHONE_NUMBER` | Twilio Phone Number (for future integrations) |
| `VAPI_API_KEY` | Vapi.ai API Key (for future integrations) |
| `RESUME_TEXT_PATH` | Path to resume file (default: `./data/resume.txt`) |
| `GITHUB_REPOS_PATH` | Path to repos directory (default: `./data/repos/`) |
| `OWNER_NAME` | Name of the persona (e.g., Daksh) |
| `ROLE` | Role of the persona (e.g., AI Developer) |

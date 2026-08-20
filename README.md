# AI Research Assistant
This application allows users to efficiently prompt an AI with memory limited to the documents they provide it with. In safety-critical applications of AI like hospital or military usage, it is essential that the AI is only pulling information from ground-truth documents and not hallucinating an answer from its weights and biases. It utilizes Retrieval-Augmented Generation (RAG), which is an efficient system for turning chunks of documents into semantically relevant vectors to be compared against a prompt vector for similarity. The most similar chunks are then included in the prompt itself. The prompt is designed to require the LLM to only draw information from the provided chunks of text, and depending on the mode, cite where its getting its answers from.

It supports two generation modes:

* **Evidence Mode** — requires citations and supporting quotes with filename and page number
* **Grounded Mode** — answers using only information from the uploaded PDFs without requiring citations

## Features

* Multi-PDF upload and indexing
* PDF text extraction with PyMuPDF
* Overlapping text chunking
* Sentence-transformer embeddings
* FAISS vector similarity search
* Persistent FAISS index and metadata
* Multi-document semantic retrieval
* OpenAI-powered answer generation
* Evidence-grounded answers with filename and page citations
* Direct supporting quotes from retrieved PDF passages
* Toggleable Evidence and Grounded generation modes
* Delete-document support with index rebuilding
* React frontend with loading states and collapsible sources
* FastAPI backend with REST endpoints
* Retrieval evaluation using Recall@1, Recall@3, and Recall@5

## Architecture

```text
                           INGESTION

                    User uploads PDF
                           |
                           v
                       PyMuPDF
                           |
                           v
                    Extracted text
                           |
                           v
                        Chunker
                           |
                           v
                  Sentence Transformer
                           |
                           v
                     Embeddings
                           |
                           v
                    FAISS Vector Index
                           |
                           +---- Metadata
                                 filename
                                 page
                                 chunk ID


                            QUERY

                     User question
                           |
                           v
                  Sentence Transformer
                           |
                           v
                    Query embedding
                           |
                           v
                      FAISS search
                           |
                           v
                 Top-K relevant chunks
                           |
                           v
                  Generation prompt
                     /           \
                    /             \
           Evidence Mode      Grounded Mode
                    \             /
                     \           /
                           v
                        OpenAI
                           |
                           v
                  Grounded response
```

## Tech Stack

### Backend

* Python
* FastAPI
* PyMuPDF
* Sentence Transformers
* FAISS
* NumPy
* OpenAI API

### Frontend

* React
* Vite
* JavaScript
* React Markdown
* CSS

## Project Structure

```text
rag-app/
├── backend/
│   ├── main.py
│   └── rag/
│       ├── pdf_parser.py
│       ├── chunker.py
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── retriever.py
│       └── generator.py
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── UploadPanel.jsx
│       │   ├── DocumentList.jsx
│       │   ├── ChatBox.jsx
│       │   └── SourceList.jsx
│       ├── api.js
│       ├── App.jsx
│       └── index.css
│
├── data/
│   ├── uploads/
│   └── indexes/
│
├── eval/
│   ├── documents/
│   ├── questions.json
│   └── evaluate.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## How the RAG Pipeline Works

### 1. PDF ingestion

Uploaded PDFs are parsed using PyMuPDF and converted into page-level text.

### 2. Chunking

Each page is split into overlapping text chunks. Chunk metadata includes:

* filename
* page number
* chunk ID
* original text

### 3. Embeddings

Each chunk is converted into a dense vector using a Sentence Transformer embedding model.

The current implementation uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### 4. Vector storage

Normalized chunk embeddings are stored in a FAISS index.

Metadata is stored alongside the index so retrieved vectors can be mapped back to their original PDF, page, and text.

The FAISS index and metadata are persisted to disk so uploaded documents remain indexed after the backend restarts.

### 5. Retrieval

When a user asks a question:

1. The question is embedded using the same embedding model.
2. FAISS performs similarity search against the stored chunk vectors.
3. The top relevant chunks are returned.
4. Those chunks become context for the generation model.

### 6. Generation

The retrieved text is passed to an OpenAI model along with one of two prompts.

#### Evidence Mode

The model must:

* use only information from retrieved PDFs
* support factual claims with citations
* include filename and page number
* provide short direct quotes for important claims

Example:

```text
Linear probes achieved greater than 90% accuracy in some deception
detection experiments [paper.pdf, p. 1].

> Evidence: "Our probes reach a maximum of >90% accuracy"
> [paper.pdf, p. 1]
```

#### Grounded Mode

The model may answer more naturally but is still restricted to information contained in the retrieved PDF passages.

No external knowledge should be used.

## Retrieval Evaluation

The retrieval system is evaluated independently from answer generation using a fixed multi-document benchmark.

The evaluation corpus includes multiple related machine-learning documents along with unrelated material to test semantic discrimination.

Current document-level retrieval performance:

| Metric   |  Score |
| -------- | -----: |
| Recall@1 | 88.57% |
| Recall@3 | 91.43% |
| Recall@5 | 94.29% |

### What the metrics mean

**Recall@1** measures whether the highest-ranked retrieved chunk comes from the correct document.

**Recall@3** measures whether at least one of the three highest-ranked chunks comes from the correct document.

**Recall@5** measures whether at least one of the five highest-ranked chunks comes from the correct document.

The evaluation index is rebuilt from a fixed set of evaluation PDFs each time so results are independent from documents uploaded through the application.

## Installation

Clone the repository:

```bash
git clone https://github.com/bhaiding/rag-app.git
cd rag-app
```

Create and activate a virtual environment if desired:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

## Environment Variables

The backend requires an OpenAI API key.

Set it in your environment:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

On macOS with zsh, you can persist the variable by adding it to:

```text
~/.zshrc
```

and then running:

```bash
source ~/.zshrc
```

Do not commit API keys to GitHub.

## Running the Application

Start the backend from the project root:

```bash
python3 -m uvicorn backend.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

In another terminal, start the frontend:

```bash
cd frontend
npm run dev
```

The frontend will typically run at:

```text
http://localhost:5173
```

## API Endpoints

### Upload a document

```text
POST /documents
```

Parses, chunks, embeds, and adds a PDF to the FAISS index.

### List documents

```text
GET /documents
```

Returns currently indexed documents and metadata.

### Ask a question

```text
POST /query
```

Example request:

```json
{
  "question": "What is multi-head attention?",
  "mode": "evidence"
}
```

Supported modes:

```text
evidence
grounded
```

### Delete a document

```text
DELETE /documents/{filename}
```

Removes a document and rebuilds the FAISS index using the remaining chunks.

## Running Retrieval Evaluation

From the repository root:

```bash
python3 -m eval.evaluate
```

The evaluator:

1. Loads a fixed collection of evaluation PDFs
2. Parses and chunks the documents
3. Creates fresh embeddings
4. Builds a fresh FAISS index
5. Runs the evaluation questions
6. Reports Recall@1, Recall@3, and Recall@5

## Future Improvements

* Compare stronger embedding models such as BGE and E5
* Benchmark different chunk sizes and overlaps
* Add reranking after initial FAISS retrieval
* Add passage-level rather than document-level retrieval evaluation
* Add automated unit and API tests
* Add authentication and user-specific document collections
* Add Docker support
* Deploy the frontend and backend
* Add streaming model responses
* Add richer PDF citation navigation

## Author

Built as a full-stack AI engineering project focused on retrieval-augmented generation, semantic search, vector databases, grounded LLM generation, and evaluation.

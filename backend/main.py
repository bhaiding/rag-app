from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil

from fastapi.middleware.cors import CORSMiddleware
from backend.rag.pdf_parser import extract_text_from_pdf
from backend.rag.chunker import chunk_pages
from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator

INDEX_DIR = Path("data/indexes")

FAISS_INDEX_PATH = INDEX_DIR / "documents.faiss"
METADATA_PATH = INDEX_DIR / "metadata.json"

INDEX_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

app = FastAPI(
    title="RAG Research Assistant",
    description="Upload PDFs and ask questions across all uploaded documents.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


embedding_model = EmbeddingModel()


if (
    FAISS_INDEX_PATH.exists()
    and METADATA_PATH.exists()
):
    vector_store = VectorStore.load(
        FAISS_INDEX_PATH,
        METADATA_PATH,
    )

    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    print(
        f"Loaded {len(vector_store)} vectors "
        "from disk."
    )

else:
    vector_store = None
    retriever = None
generator = None

def build_uploaded_documents(vector_store):
    if vector_store is None:
        return []

    documents = {}

    for item in vector_store.metadata:
        filename = item.get("filename")
        page = item.get("page")

        if not filename:
            continue

        if filename not in documents:
            documents[filename] = {
                "filename": filename,
                "pages": set(),
                "chunks": 0,
            }

        documents[filename]["chunks"] += 1

        if page is not None:
            documents[filename]["pages"].add(page)

    result = []

    for document in documents.values():
        result.append(
            {
                "filename": document["filename"],
                "pages": len(document["pages"]),
                "chunks": document["chunks"],
            }
        )

    return result


uploaded_documents = build_uploaded_documents(vector_store)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "RAG Research Assistant API is running.",
        "uploaded_documents": uploaded_documents,
    }


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    global vector_store
    global retriever

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = extract_text_from_pdf(file_path)

    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=200,
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the PDF.",
        )

    # Add document metadata to every chunk
    for chunk in chunks:
        chunk["filename"] = file.filename

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.embed_texts(
        chunk_texts
    )

    # Create the FAISS index only once
    if vector_store is None:
        vector_store = VectorStore(
            embedding_dim=embeddings.shape[1]
        )

    # Add this document to the existing index
    vector_store.add(
        embeddings,
        chunks,
    )
    vector_store.save(
        FAISS_INDEX_PATH,
        METADATA_PATH,
    )

    # Retriever continues using the same growing vector store
    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    uploaded_documents.clear()
    uploaded_documents.extend(
        build_uploaded_documents(vector_store)
    )

    return {
        "filename": file.filename,
        "pages": len(pages),
        "chunks_added": len(chunks),
        "total_vectors": len(vector_store),
        "total_documents": len(uploaded_documents),
        "message": "Document added to index successfully.",
    }


@app.post("/query")
def query_documents(request: QueryRequest):
    global generator

    if retriever is None:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one PDF before asking questions.",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    results = retriever.retrieve(
        question,
        k=5,
    )

    if generator is None:
        generator = Generator()

    answer = generator.generate_answer(
        question,
        results,
    )

    sources = []

    for result in results:
        sources.append(
            {
                "filename": result["filename"],
                "page": result["page"],
                "chunk_id": result["chunk_id"],
                "score": result["score"],
                "text": result["text"],
            }
        )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }


@app.get("/documents")
def get_documents():
    return {
        "documents": uploaded_documents,
        "total_documents": len(uploaded_documents),
        "total_vectors": (
            len(vector_store)
            if vector_store is not None
            else 0
        ),
    }
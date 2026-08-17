from backend.rag.pdf_parser import extract_text_from_pdf
from backend.rag.chunker import chunk_pages
from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator


pdf_path = "data/uploads/test.pdf"

# 1. Parse PDF
pages = extract_text_from_pdf(pdf_path)

print(f"Extracted {len(pages)} pages.")


# 2. Chunk document
chunks = chunk_pages(
    pages,
    chunk_size=1000,
    overlap=200,
)

print(f"Created {len(chunks)} chunks.")


# 3. Load embedding model
embedding_model = EmbeddingModel()


# 4. Embed document chunks
chunk_texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.embed_texts(
    chunk_texts
)

print(
    f"Created embeddings: "
    f"{embeddings.shape}"
)


# 5. Build FAISS vector store
vector_store = VectorStore(
    embedding_dim=embeddings.shape[1]
)

vector_store.add(
    embeddings,
    chunks,
)

print(
    f"Stored {len(vector_store)} vectors."
)


# 6. Create retriever
retriever = Retriever(
    embedding_model=embedding_model,
    vector_store=vector_store,
)


# 7. Ask question
question = (
    "How accurately can internal activations "
    "detect deception?"
)


# 8. Retrieve relevant chunks
results = retriever.retrieve(
    question,
    k=5,
)

print()
print("Retrieved chunks:")

for result in results:
    print(
        f"Page {result['page']} "
        f"- Score {result['score']:.4f}"
    )


# 9. Create LLM generator
generator = Generator()


# 10. Generate final answer
answer = generator.generate_answer(
    question,
    results,
)

print()
print("QUESTION:")
print(question)

print()
print("ANSWER:")
print(answer)
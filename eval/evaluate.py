import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.rag.pdf_parser import extract_text_from_pdf
from backend.rag.chunker import chunk_pages
from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import VectorStore
from backend.rag.retriever import Retriever


QUESTIONS_PATH = Path("eval/questions.json")

# These are the ONLY documents used during evaluation.
EVAL_DOCUMENTS = [
    Path("eval/documents/Calculus.pdf"),
    Path("eval/documents/Logistic_Regression.pdf"),
    Path("eval/documents/CNN.pdf"),
    Path("eval/documents/RNN.pdf"),
    Path("eval/documents/Transformer.pdf"),
]


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_questions():
    """
    Load evaluation questions from JSON.
    """

    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_eval_vector_store(embedding_model):
    """
    Build a fresh vector store from the fixed evaluation PDFs.

    Nothing is loaded from data/indexes/.
    Nothing is saved to data/indexes/.
    """

    all_chunks = []

    print("Building evaluation index...")
    print()

    for pdf_path in EVAL_DOCUMENTS:
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Evaluation PDF not found: {pdf_path}"
            )

        print(f"Processing: {pdf_path.name}")

        pages = extract_text_from_pdf(
            pdf_path
        )

        chunks = chunk_pages(
            pages,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )

        # Add filename metadata so we know
        # which PDF every chunk came from.
        for chunk in chunks:
            chunk["filename"] = pdf_path.name

        all_chunks.extend(chunks)

        print(
            f"  Pages: {len(pages)}"
        )

        print(
            f"  Chunks: {len(chunks)}"
        )

    if not all_chunks:
        raise ValueError(
            "No chunks were created from the evaluation documents."
        )

    print()
    print(
        f"Total chunks: {len(all_chunks)}"
    )

    chunk_texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    print("Creating embeddings...")

    embeddings = embedding_model.embed_texts(
        chunk_texts
    )

    print(
        f"Embedding matrix: {embeddings.shape}"
    )

    vector_store = VectorStore(
        embedding_dim=embeddings.shape[1]
    )

    vector_store.add(
        embeddings,
        all_chunks,
    )

    print(
        f"Stored {len(vector_store)} vectors."
    )

    print()

    return vector_store


def is_correct_result(
    result,
    question_data,
):
    """
    A result is correct if it comes from
    the expected PDF.
    """

    return (
        result.get("filename")
        == question_data["expected_filename"]
    )


def calculate_recall(
    retriever,
    questions,
    k,
):
    """
    Calculate document-level Recall@k.
    """

    correct = 0

    for question_data in questions:
        results = retriever.retrieve(
            question_data["question"],
            k=k,
        )

        found_correct_document = any(
            is_correct_result(
                result,
                question_data,
            )
            for result in results
        )

        if found_correct_document:
            correct += 1

    return correct / len(questions)


def print_question_results(
    retriever,
    questions,
    k=5,
):
    """
    Show detailed retrieval results
    for every evaluation question.
    """

    for index, question_data in enumerate(
        questions,
        start=1,
    ):
        question = question_data["question"]

        expected_filename = question_data[
            "expected_filename"
        ]

        results = retriever.retrieve(
            question,
            k=k,
        )

        found_correct_document = any(
            is_correct_result(
                result,
                question_data,
            )
            for result in results
        )

        status = (
            "PASS"
            if found_correct_document
            else "FAIL"
        )

        print()
        print("=" * 80)

        print(
            f"Question {index}: {status}"
        )

        print(
            f"Question: {question}"
        )

        print(
            f"Expected document: "
            f"{expected_filename}"
        )

        print()

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"{result.get('filename')} "
                f"| page {result.get('page')} "
                f"| score "
                f"{result.get('score', 0):.4f}"
            )


def main():
    questions = load_questions()

    if not questions:
        raise ValueError(
            "No evaluation questions found."
        )

    print(
        f"Loaded {len(questions)} "
        "evaluation questions."
    )

    print()

    embedding_model = EmbeddingModel()

    vector_store = build_eval_vector_store(
        embedding_model
    )

    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    

    

    
    print("DETAILED RESULTS")

    print_question_results(
        retriever,
        questions,
        k=5,
    )
    print()
    for k in [1, 3, 5]:
        recall = calculate_recall(
            retriever,
            questions,
            k,
        )
    print("DOCUMENT RETRIEVAL EVALUATION")
    print("-" * 40)
    
    for k in [1, 3, 5]:
        recall = calculate_recall(
            retriever,
            questions,
            k,
        )
        print(
            f"Recall@{k}: "
            f"{recall:.2%}"
        )


if __name__ == "__main__":
    main()
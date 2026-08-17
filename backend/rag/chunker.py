from typing import List, Dict


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> List[Dict]:
    """
    Split page text into overlapping character-based chunks.

    Args:
        pages:
            Output from extract_text_from_pdf().
            Expected format:
            [
                {
                    "page": 1,
                    "text": "..."
                },
                ...
            ]

        chunk_size:
            Maximum number of characters per chunk.

        overlap:
            Number of characters shared between consecutive chunks.

    Returns:
        A list of chunk dictionaries:
        [
            {
                "chunk_id": 0,
                "page": 1,
                "text": "..."
            },
            ...
        ]
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    chunk_id = 0

    for page in pages:
        page_number = page["page"]
        text = page["text"].strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "text": chunk_text,
                    }
                )

                chunk_id += 1

            if end >= len(text):
                break

            start += chunk_size - overlap

    return chunks


if __name__ == "__main__":
    sample_pages = [
        {
            "page": 1,
            "text": (
                "This is a sample first page. "
                "It contains enough text to demonstrate how chunking works. "
                "The chunker splits long pieces of text into smaller overlapping sections."
            ),
        },
        {
            "page": 2,
            "text": (
                "This is the second page. "
                "Later, each chunk will be converted into an embedding vector."
            ),
        },
    ]

    chunks = chunk_pages(
        sample_pages,
        chunk_size=80,
        overlap=20,
    )

    for chunk in chunks:
        print(
            f"Chunk {chunk['chunk_id']} "
            f"(Page {chunk['page']}):"
        )
        print(chunk["text"])
        print("-" * 50)
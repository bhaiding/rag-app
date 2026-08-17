# backend/rag/pdf_parser.py

from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A list of dictionaries in the form:
        [
            {
                "page": 1,
                "text": "Page text..."
            },
            ...
        ]

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is not a PDF.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.suffix}")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

    return pages


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pdf_parser.py <path_to_pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    extracted_pages = extract_text_from_pdf(pdf_file)

    print(f"Extracted {len(extracted_pages)} pages.\n")

    for page in extracted_pages:
        print(f"--- PAGE {page['page']} ---")
        print(page["text"][:500])
        print()
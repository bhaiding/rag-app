import os
from typing import List, Dict

from openai import OpenAI


DEFAULT_MODEL = "gpt-5-mini"


class Generator:
    def __init__(self, model: str = DEFAULT_MODEL):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def build_context(
        self,
        retrieved_chunks: List[Dict],
    ) -> str:
        context_parts = []

        for i, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            filename = chunk.get(
                "filename",
                "Unknown document",
            )

            page = chunk.get(
                "page",
                "unknown",
            )

            text = chunk.get(
                "text",
                "",
            )

            context_parts.append(
                f"""
SOURCE {i}
Filename: {filename}
Page: {page}
Text:
{text}
""".strip()
            )

        return "\n\n".join(context_parts)

    def build_evidence_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        return f"""
You are an evidence-grounded research assistant.

Answer the user's question using ONLY the provided PDF sources.

FORMAT YOUR RESPONSE AS CLEAN MARKDOWN.

STRICT RULES:

1. Answer the question directly and clearly.

2. Every factual claim must be supported by the provided PDF sources.

3. Put a citation immediately after each factual claim using this format:

   [Filename.pdf, p. X]

4. For the most important claims, include a short direct quote on a separate line:

   > Evidence: "short exact quote" [Filename.pdf, p. X]

5. Do not invent quotes.

6. Do not use outside knowledge.

7. Do not make factual claims that cannot be supported by the provided sources.

8. If the provided sources do not contain enough information, say so clearly.

9. Use short paragraphs, headings, bullet points, and numbered steps when helpful.

10. Do not repeat the same evidence unnecessarily.

11. Use direct quotes selectively. Usually 2-4 important quotes are enough.

PROVIDED SOURCES:

{context}

USER QUESTION:

{question}
"""

    def build_grounded_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        return f"""
You are a research assistant answering questions about uploaded PDF documents.

Answer the user's question using ONLY information contained in the provided PDF sources.

FORMAT YOUR RESPONSE AS CLEAN MARKDOWN.

STRICT RULES:

1. Answer the question directly and clearly.

2. You may ONLY use information contained in the provided sources.

3. Do NOT use outside knowledge, even if you know the answer.

4. Citations are NOT required.

5. Direct quotes are NOT required.

6. Explain the material naturally and clearly rather than constantly referring to the documents.

7. You may summarize, combine, and explain information from multiple retrieved passages.

8. Do not make claims that cannot be supported by the provided sources.

9. If the sources do not contain enough information to answer the question, say:

   "The provided documents do not contain enough information to answer this."

10. Use headings, paragraphs, bullets, equations, and numbered steps when helpful.

PROVIDED SOURCES:

{context}

USER QUESTION:

{question}
"""

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict],
        mode: str = "evidence",
    ) -> str:
        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not retrieved_chunks:
            return (
                "I could not find enough relevant information "
                "in the uploaded documents to answer this question."
            )

        if mode not in {"evidence", "grounded"}:
            raise ValueError(
                f"Invalid generation mode: {mode}"
            )

        context = self.build_context(
            retrieved_chunks
        )

        if mode == "evidence":
            prompt = self.build_evidence_prompt(
                question,
                context,
            )
        else:
            prompt = self.build_grounded_prompt(
                question,
                context,
            )

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text
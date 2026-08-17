import os
from typing import List, Dict

from openai import OpenAI


DEFAULT_MODEL = "gpt-5-mini"


class Generator:
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Create an LLM generator.

        Requires the OPENAI_API_KEY environment variable.
        """
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def build_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Convert retrieved chunks into formatted source context.
        """

        context_parts = []

        for i, chunk in enumerate(retrieved_chunks, start=1):
            page = chunk.get("page", "unknown")
            text = chunk.get("text", "")

            context_parts.append(
                f"[Source {i} - Page {page}]\n{text}"
            )

        return "\n\n".join(context_parts)

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict],
    ) -> str:
        """
        Generate an answer using only the retrieved document chunks.
        """

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        if not retrieved_chunks:
            return "I could not find relevant information in the uploaded documents."

        context = self.build_context(retrieved_chunks)

        prompt = f"""
You are a research assistant answering questions about uploaded documents.

Answer the user's question using only the provided sources.

If the sources do not contain enough information to answer the question,
say that clearly.

Cite relevant sources in your answer using the format [Source 1],
[Source 2], etc.

SOURCES:

{context}

USER QUESTION:

{question}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text
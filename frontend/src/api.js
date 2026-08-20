const API_BASE_URL = "http://127.0.0.1:8000";


export async function getDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to load documents.");
  }

  return response.json();
}


export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Failed to upload document."
    );
  }

  return response.json();
}


export async function askQuestion(question, mode) {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      mode,
    }),
  });

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Failed to ask question."
    );
  }

  return response.json();
}


export async function deleteDocument(filename) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(filename)}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Failed to delete document."
    );
  }

  return response.json();
}
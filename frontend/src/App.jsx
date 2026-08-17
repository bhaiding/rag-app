import { useEffect, useState } from "react";
import {
  askQuestion,
  getDocuments,
  uploadDocument,
} from "./api";

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      const data = await getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload() {
    if (!selectedFile) {
      setError("Choose a PDF first.");
      return;
    }

    try {
      setError("");
      setUploading(true);

      await uploadDocument(selectedFile);
      setSelectedFile(null);

      await loadDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleQuestion(event) {
    event.preventDefault();

    if (!question.trim()) {
      setError("Enter a question.");
      return;
    }

    try {
      setError("");
      setAsking(true);
      setAnswer("");
      setSources([]);

      const data = await askQuestion(question);

      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <main>
      <h1>AI Research Assistant</h1>

      <section>
        <h2>Upload Documents</h2>

        <input
          type="file"
          accept=".pdf"
          onChange={(event) => {
            setSelectedFile(event.target.files[0]);
          }}
        />

        <button
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Upload PDF"}
        </button>
      </section>

      <section>
        <h2>Uploaded Documents</h2>

        {documents.length === 0 ? (
          <p>No documents uploaded.</p>
        ) : (
          <ul>
            {documents.map((document) => (
              <li key={document.filename}>
                {document.filename} — {document.pages} pages —{" "}
                {document.chunks} chunks
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>Ask a Question</h2>

        <form onSubmit={handleQuestion}>
          <input
            type="text"
            value={question}
            placeholder="Ask something about your documents..."
            onChange={(event) => {
              setQuestion(event.target.value);
            }}
          />

          <button
            type="submit"
            disabled={asking}
          >
            {asking ? "Thinking..." : "Ask"}
          </button>
        </form>
      </section>

      {error && (
        <section>
          <p>{error}</p>
        </section>
      )}

      {answer && (
        <section>
          <h2>Answer</h2>
          <p>{answer}</p>
        </section>
      )}

      {sources.length > 0 && (
        <section>
          <h2>Sources</h2>

          {sources.map((source, index) => (
            <div key={`${source.filename}-${source.chunk_id}`}>
              <h3>Source {index + 1}</h3>

              <p>
                {source.filename} — Page {source.page}
              </p>

              <p>
                Similarity: {source.score.toFixed(3)}
              </p>

              <p>{source.text}</p>
            </div>
          ))}
        </section>
      )}
    </main>
  );
}

export default App;
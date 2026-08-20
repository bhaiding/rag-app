import { useEffect, useState } from "react";

import {
  askQuestion,
  deleteDocument,
  getDocuments,
  uploadDocument,
} from "./api";

import UploadPanel from "./components/UploadPanel";
import DocumentList from "./components/DocumentList";
import ChatBox from "./components/ChatBox";
import SourceList from "./components/SourceList";


function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const [mode, setMode] = useState("evidence");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  const [deletingFilename, setDeletingFilename] =
    useState(null);


  async function loadDocuments() {
    try {
      const data = await getDocuments();

      setDocuments(data.documents);
    } catch (err) {
      setError(err.message);
    }
  }


  async function handleDelete(filename) {
    try {
      setError("");
      setDeletingFilename(filename);

      await deleteDocument(filename);

      await loadDocuments();

      setAnswer("");
      setSources([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingFilename(null);
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

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Enter a question.");
      return;
    }

    try {
      setError("");
      setAsking(true);

      setAnswer("");
      setSources([]);

      const data = await askQuestion(
        trimmedQuestion,
        mode,
      );

      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  }


  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>AI Research Assistant</h1>

          <p>
            Upload research papers and ask questions across your documents.
          </p>
        </div>
      </header>

      <div className="app-layout">
        <aside className="sidebar">
          <UploadPanel
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            handleUpload={handleUpload}
            uploading={uploading}
          />

          <DocumentList
            documents={documents}
            handleDelete={handleDelete}
            deletingFilename={deletingFilename}
          />
        </aside>

        <main className="main-content">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <ChatBox
            question={question}
            setQuestion={setQuestion}
            handleQuestion={handleQuestion}
            asking={asking}
            answer={answer}
            mode={mode}
            setMode={setMode}
          />

          <SourceList
            sources={sources}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
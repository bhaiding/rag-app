function DocumentList({
  documents,
  handleDelete,
  deletingFilename,
}) {
  return (
    <section>
      <h2>Uploaded Documents</h2>

      {documents.length === 0 ? (
        <p>No documents uploaded.</p>
      ) : (
        <ul className="document-list">
          {documents.map((document) => (
            <li
              className="document-item"
              key={document.filename}
            >
              <div>
                <strong>
                  {document.filename}
                </strong>

                <div className="document-meta">
                  {document.pages} pages ·{" "}
                  {document.chunks} chunks
                </div>
              </div>

              <button
                className="delete-button"
                onClick={() =>
                  handleDelete(document.filename)
                }
                disabled={
                  deletingFilename ===
                  document.filename
                }
              >
                {deletingFilename ===
                document.filename
                  ? "Deleting..."
                  : "Delete"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default DocumentList;
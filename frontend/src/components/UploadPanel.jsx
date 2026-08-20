function UploadPanel({
  selectedFile,
  setSelectedFile,
  handleUpload,
  uploading,
}) {
  return (
    <section>
      <h2>Upload Documents</h2>

      <input
        type="file"
        accept=".pdf"
        disabled={uploading}
        onChange={(event) => {
          setSelectedFile(event.target.files[0] || null);
        }}
      />

      <button
        onClick={handleUpload}
        disabled={uploading || !selectedFile}
      >
        {uploading ? "Processing PDF..." : "Upload PDF"}
      </button>

      {selectedFile && !uploading && (
        <p className="status-text">
          Selected: {selectedFile.name}
        </p>
      )}

      {uploading && (
        <div className="loading-row">
          <div className="spinner" />
          <span>
            Extracting text, chunking, and creating embeddings...
          </span>
        </div>
      )}
    </section>
  );
}

export default UploadPanel;
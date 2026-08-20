function SourceList({ sources }) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <section className="sources-section">
      <h2>Sources</h2>

      <div className="sources-list">
        {sources.map((source, index) => (
          <details
            className="source-card"
            key={`${source.filename}-${source.chunk_id}-${index}`}
          >
            <summary>
              <span>
                Source {index + 1}: {source.filename}
              </span>

              <span className="source-meta">
                Page {source.page} · {source.score.toFixed(3)}
              </span>
            </summary>

            <div className="source-content">
              <p>{source.text}</p>
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

export default SourceList;
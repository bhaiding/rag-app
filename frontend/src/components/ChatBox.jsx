import ReactMarkdown from "react-markdown";

function ChatBox({
  question,
  setQuestion,
  handleQuestion,
  asking,
  answer,
  mode,
  setMode,
}) {
  return (
    <section>
      <div className="question-header">
        <h2>Ask a Question</h2>

        <div className="mode-toggle">
          <button
            type="button"
            className={
              mode === "grounded"
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() => {
              setMode("grounded");
            }}
          >
            Grounded
          </button>

          <button
            type="button"
            className={
              mode === "evidence"
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() => {
              setMode("evidence");
            }}
          >
            Evidence
          </button>
        </div>
      </div>

      <p className="mode-description">
        {mode === "evidence"
          ? "Answers use only your PDFs and include citations and supporting quotes."
          : "Answers use only your PDFs, without requiring citations."}
      </p>

      <form onSubmit={handleQuestion}>
        <input
          type="text"
          value={question}
          disabled={asking}
          placeholder="Ask something about your documents..."
          onChange={(event) => {
            setQuestion(event.target.value);
          }}
        />

        <button
          type="submit"
          disabled={asking || !question.trim()}
        >
          {asking ? "Thinking..." : "Ask"}
        </button>
      </form>

      {asking && (
        <div className="loading-row">
          <div className="spinner" />

          <span>
            {mode === "evidence"
              ? "Retrieving passages and gathering evidence..."
              : "Retrieving relevant information and generating an answer..."}
          </span>
        </div>
      )}

      {answer && !asking && (
        <div className="answer-box">
          <h2>Answer</h2>

          <div className="answer-content">
            <ReactMarkdown>
              {answer}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </section>
  );
}

export default ChatBox;
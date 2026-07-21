"use client";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return <p className="state-message" role="status">{label}</p>;
}

export function ErrorState({ message }: { message: string }) {
  return <p className="state-message error-message" role="alert">{message}</p>;
}

export function PageHeader({ eyebrow, title, description }: { eyebrow?: string; title: string; description?: string }) {
  return (
    <header className="page-header">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h1>{title}</h1>
      {description && <p className="muted">{description}</p>}
    </header>
  );
}

export function Shell({ children }: { children: React.ReactNode }) {
  return <main className="shell">{children}</main>;
}

export function AssistantPanel({
  question,
  setQuestion,
  onSend,
  answer,
  loading,
  error,
}: {
  question: string;
  setQuestion: (value: string) => void;
  onSend: () => void;
  answer?: string;
  loading: boolean;
  error?: string;
}) {
  return (
    <section className="panel assistant-panel">
      <div>
        <p className="eyebrow">Queue Operations Assistant</p>
        <h2>Have a question?</h2>
      </div>
      <div className="inline-form">
        <label className="sr-only" htmlFor="assistant-question">Question</label>
        <input id="assistant-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about your queue…" />
        <button type="button" onClick={onSend} disabled={loading || !question.trim()}>{loading ? "Sending…" : "Send"}</button>
      </div>
      {error && <ErrorState message={error} />}
      {answer && <p className="assistant-answer">{answer}</p>}
    </section>
  );
}

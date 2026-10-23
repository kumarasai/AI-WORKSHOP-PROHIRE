
import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const bottomRef = useRef(null);

  // Create the first session when the app opens.
  useEffect(() => {
    startNewChat();
  }, []);

  // Keep the latest message visible.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function startNewChat() {
    setLoading(false);
    setError("");
    setInput("");
    setMessages([]);
    setSessionId("");

    try {
      const response = await fetch(`${API_URL}/api/sessions`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Could not create a new chat.");
      }

      const data = await response.json();
      setSessionId(data.session_id);
    } catch {
      setError(
        "Cannot connect to the backend. Check whether FastAPI is running."
      );
    }
  }

  async function sendMessage(event) {
    event.preventDefault();

    const question = input.trim();

    if (!question || !sessionId || loading) {
      return;
    }

    setError("");
    setInput("");
    setMessages((previous) => [
      ...previous,
      { role: "user", content: question },
    ]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get an AI response."
        );
      }

      // Use the complete history returned by the backend.
      setMessages(data.messages);
    } catch (err) {
      setError(err.message || "Something went wrong.");

      // Keep the user's question visible if the request fails.
      // Do not invent an AI response.
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="chat-card">
        <header className="chat-header">
          <div>
            <h1>AI Chatbot</h1>
            <p>Conversation Memory Demo</p>
          </div>

          <button
            className="new-chat"
            onClick={startNewChat}
            disabled={loading}
          >
            + New Chat
          </button>
        </header>

        <div className="session-info">
          Session:{" "}
          <span>{sessionId || "Creating session..."}</span>
        </div>

        <section
          className="messages"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.length === 0 && !loading && (
            <div className="welcome">
              <h2>Hi! 👋</h2>
              <p>Ask a question to start your conversation.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${index}-${message.role}`}
              className={`message ${message.role}`}
            >
              <strong>
                {message.role === "user" ? "You" : "AI"}
              </strong>
              <p>{message.content}</p>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <strong>AI</strong>
              <p>Thinking...</p>
            </div>
          )}

          <div ref={bottomRef} />
        </section>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <form className="chat-form" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type your message..."
            aria-label="Your message"
            disabled={loading || !sessionId}
          />

          <button
            type="submit"
            disabled={loading || !sessionId || !input.trim()}
          >
            Send
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;

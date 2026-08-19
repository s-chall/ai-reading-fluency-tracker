import { useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const DEFAULT_PASSAGE =
  "The sun was warm and the wind was soft. A small dog ran across the " +
  "yard and jumped over a log. Birds sang in the tall green tree while " +
  "the dog looked for a place to rest.";

export default function App() {
  const [passage, setPassage] = useState(DEFAULT_PASSAGE);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  const startTime = useRef(0);

  async function startRecording() {
    setError(null);
    setResult(null);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunks.current = [];

    recorder.ondataavailable = (e) => chunks.current.push(e.data);
    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      submitRecording(Date.now() - startTime.current);
    };

    mediaRecorder.current = recorder;
    startTime.current = Date.now();
    recorder.start();
    setRecording(true);
  }

  function stopRecording() {
    mediaRecorder.current?.stop();
    setRecording(false);
  }

  async function submitRecording(elapsedMs) {
    setLoading(true);
    try {
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      const form = new FormData();
      form.append("audio", blob, "reading.webm");
      form.append("passage", passage);
      form.append("elapsed_seconds", (elapsedMs / 1000).toFixed(2));

      const res = await fetch(`${API_URL}/score`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>AI Reading Fluency Tracker</h1>
      <p className="subtitle">
        Read the passage aloud, then stop the recording to get words-correct-per-minute
        and an error breakdown.
      </p>

      <textarea
        className="passage"
        value={passage}
        onChange={(e) => setPassage(e.target.value)}
        disabled={recording || loading}
        rows={5}
      />

      <div className="controls">
        {!recording ? (
          <button onClick={startRecording} disabled={loading}>
            ● Start Recording
          </button>
        ) : (
          <button className="stop" onClick={stopRecording}>
            ■ Stop Recording
          </button>
        )}
      </div>

      {loading && <p className="status">Transcribing and scoring…</p>}
      {error && <p className="status error">{error}</p>}

      {result && (
        <div className="results">
          <div className="stats">
            <Stat label="WCPM" value={result.wcpm} />
            <Stat label="Words Correct" value={`${result.words_correct} / ${result.word_count}`} />
            <Stat label="Errors" value={result.error_count} />
            <Stat label="Time (s)" value={result.elapsed_seconds} />
          </div>

          <h3>Transcript</h3>
          <p className="transcript">{result.transcript}</p>

          {result.errors.length > 0 && (
            <>
              <h3>Error Breakdown</h3>
              <ul className="errors">
                {result.errors.map((e, i) => (
                  <li key={i} className={`error-${e.type}`}>
                    <span className="tag">{e.type}</span>{" "}
                    {e.type === "substitution" ? (
                      <>
                        said <strong>{e.word}</strong> for <strong>{e.expected}</strong>
                      </>
                    ) : (
                      <strong>{e.word}</strong>
                    )}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

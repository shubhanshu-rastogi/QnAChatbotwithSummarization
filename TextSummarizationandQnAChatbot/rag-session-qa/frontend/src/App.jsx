import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [summary, setSummary] = useState('')
  const [citations, setCitations] = useState([])
  const [summaryCitations, setSummaryCitations] = useState([])
  const [retrievalContext, setRetrievalContext] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const resetOutputs = () => {
    setAnswer('')
    setSummary('')
    setCitations([])
    setSummaryCitations([])
    setRetrievalContext([])
  }

  const handleUpload = async () => {
    setError('')
    setStatus('')
    resetOutputs()

    if (!file) {
      setError('Please select a file to upload.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setSessionId(data.session_id)
      setStatus(data.message)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async () => {
    setError('')
    setAnswer('')
    setCitations([])
    setRetrievalContext([])

    if (!sessionId) {
      setError('Please upload a document first.')
      return
    }
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question })
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Ask failed')
      }

      setAnswer(data.answer)
      setCitations(data.citations || [])
      setRetrievalContext(data.retrieval_context || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSummary = async () => {
    setError('')
    setSummary('')
    setSummaryCitations([])

    if (!sessionId) {
      setError('Please upload a document first.')
      return
    }

    try {
      setLoading(true)
      const res = await fetch(`${API_URL}/summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Summary failed')
      }

      setSummary(data.summary)
      setSummaryCitations(data.citations || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Session RAG Document Q&amp;A</h1>
        <p>Upload a document, ask questions, and generate a summary with citations.</p>
      </header>

      <section className="card">
        <h2>1. Upload Document</h2>
        <div className="row">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button onClick={handleUpload} disabled={loading}>
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        {status && <div className="success">{status}</div>}
        {sessionId && (
          <div className="session">
            Current session: <span>{sessionId}</span>
          </div>
        )}
      </section>

      <section className="card">
        <h2>2. Ask a Question</h2>
        <div className="row">
          <input
            type="text"
            placeholder="Enter your question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={handleAsk} disabled={loading}>
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>
        <div className="row">
          <textarea
            className="text-box"
            placeholder="Answer will appear here"
            value={answer}
            readOnly
          />
        </div>
        {citations.length > 0 && (
          <div className="output">
            <h3>Citations</h3>
            <ul className="list">
              {citations.map((c) => (
                <li key={c.id}>
                  <strong>{c.id}</strong>: {c.snippet}
                </li>
              ))}
            </ul>
          </div>
        )}
        {retrievalContext.length > 0 && (
          <div className="output">
            <h3>Retrieval Context</h3>
            <ul className="list">
              {retrievalContext.map((ctx, idx) => (
                <li key={idx}>{ctx}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="card">
        <h2>3. Summarise</h2>
        <div className="row">
          <button onClick={handleSummary} disabled={loading}>
            {loading ? 'Summarising...' : 'Summarise'}
          </button>
          <textarea
            className="text-box"
            placeholder="Summary will appear here"
            value={summary}
            readOnly
          />
        </div>
        {summaryCitations.length > 0 && (
          <div className="output">
            <h3>Summary Citations</h3>
            <ul className="list">
              {summaryCitations.map((c) => (
                <li key={c.id}>
                  <strong>{c.id}</strong>: {c.snippet}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {error && <div className="error">{error}</div>}

      <footer className="footer">
        Session-based: a new upload clears the previous vectors.
      </footer>
    </div>
  )
}

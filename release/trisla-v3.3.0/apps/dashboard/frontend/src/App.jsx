import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState({ loading: true, data: null, error: null })

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/status')
        if (!response.ok) throw new Error('Failed to fetch status')
        const data = await response.json()
        setStatus({ loading: false, data, error: null })
      } catch (error) {
        setStatus({ loading: false, data: null, error: error.message })
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧩 TriSLA Dashboard v3.2.4</h1>
        <p>Monitoramento e Observabilidade NASP</p>
      </header>
      <main className="app-main">
        {status.loading && <p>Carregando...</p>}
        {status.error && <p className="error">Erro: {status.error}</p>}
        {status.data && (
          <div className="status-card">
            <h2>Status do Sistema</h2>
            <pre>{JSON.stringify(status.data, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  )
}

export default App



import React, {useEffect, useState} from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'

function Card({title, children}){
  return <div className="card"><h3>{title}</h3>{children}</div>
}

function Overview(){
  return (
    <div>
      <Card title="Welcome">
        <p>TriSLA Dashboard v3.2.3 — connected to NASP via SSH tunnels + remote kubectl port-forward.</p>
      </Card>
    </div>
  )
}

function Metrics({status}){
  const [result, setResult] = useState(null)
  const disabled = status.prometheus!=='online'
  const query = 'up'

  async function run(){
    const url = `/api/promql/query?query=${encodeURIComponent(query)}`
    const r = await fetch(url)
    setResult(await r.json())
  }

  return (
    <div>
      <Card title="Prometheus Query">
        <p>Query: <code>{query}</code></p>
        <button className="btn" disabled={disabled} onClick={run}>Run</button>
        <pre style={{whiteSpace:'pre-wrap'}}>{result? JSON.stringify(result, null, 2) : '—'}</pre>
      </Card>
    </div>
  )
}

function SliceNPL({status}){
  const [intent, setIntent] = useState('remote_surgery')
  const [resp, setResp] = useState(null)
  const disabled = status.sem_nsmf!=='online'
  async function submit(){
    const r = await fetch('/api/slices/npl', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({intent})})
    setResp(await r.json())
  }
  return (
    <div>
      <Card title="Create Slice (NPL)">
        <label>Intent</label>
        <input value={intent} onChange={e=>setIntent(e.target.value)} />
        <button className="btn" disabled={disabled} onClick={submit}>Submit</button>
        <pre>{resp? JSON.stringify(resp,null,2) : '—'}</pre>
      </Card>
    </div>
  )
}

function SliceGST({status}){
  const [gst, setGst] = useState('eMBB')
  const [resp, setResp] = useState(null)
  const disabled = status.sem_nsmf!=='online'
  async function submit(){
    const r = await fetch('/api/slices/gst', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({template:gst})})
    setResp(await r.json())
  }
  return (
    <div>
      <Card title="Create Slice (GST)">
        <label>GST Template</label>
        <select value={gst} onChange={e=>setGst(e.target.value)}>
          <option>eMBB</option>
          <option>URLLC</option>
          <option>mMTC</option>
        </select>
        <button className="btn" disabled={disabled} onClick={submit}>Submit</button>
        <pre>{resp? JSON.stringify(resp,null,2) : '—'}</pre>
      </Card>
    </div>
  )
}

function App(){
  const [status, setStatus] = useState({prometheus:'offline', sem_nsmf:'offline'})
  async function refresh(){
    try{
      const r = await fetch('/api/status')
      setStatus(await r.json())
    }catch(_){ /* ignore */ }
  }
  useEffect(()=>{ refresh(); const id=setInterval(refresh, 8000); return ()=>clearInterval(id)},[])
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar status={status} />
        <div className="content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/metrics" element={<Metrics status={status} />} />
            <Route path="/slices-npl" element={<SliceNPL status={status} />} />
            <Route path="/slices-gst" element={<SliceGST status={status} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)

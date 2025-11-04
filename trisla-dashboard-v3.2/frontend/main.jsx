import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Sidebar from "./components/Sidebar.jsx";
import Slices from "./pages/Slices.jsx";

function App() {
  const [status, setStatus] = useState({prometheus: "unknown", sem_nsmf: "unknown"});
  async function refresh() {
    try {
      const r = await fetch("http://localhost:5000/api/status");
      const j = await r.json();
      setStatus(j);
    } catch {}
  }
  useEffect(() => { refresh(); const id = setInterval(refresh, 10000); return () => clearInterval(id); }, []);
  return (
    <div style={{display:"flex", minHeight:"100vh", background:"#0b1730", color:"#e6eefc"}}>
      <Sidebar status={status} />
      <div style={{padding:"24px", flex:"1"}}>
        <h1 style={{marginTop:0}}>TriSLA Dashboard 3.2</h1>
        <p>Prometheus: <b style={{color: status.prometheus==='online'?'#7CFC00':'#ff8080'}}>{status.prometheus}</b> | SEM-NSMF: <b style={{color: status.sem_nsmf==='online'?'#7CFC00':'#ff8080'}}>{status.sem_nsmf}</b></p>
        <Slices enabledNPL={status.sem_nsmf==='online'} enabledGST={status.sem_nsmf==='online'} metricsEnabled={status.prometheus==='online'} />
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")).render(<App />);

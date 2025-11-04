import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import Sidebar from "./components/Sidebar.jsx";

function App() {
  const [status, setStatus] = useState({ prometheus: "unknown", sem_nsmf: "unknown", version: "" });

  async function refresh() {
    try {
      const r = await fetch("http://localhost:5000/api/status");
      const j = await r.json();
      setStatus(j);
    } catch (e) {}
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 8000);
    return () => clearInterval(id);
  }, []);

  const online = (v) => v === "online";

  return (
    <div style={{display:"flex",minHeight:"100vh",background:"#0b1730",color:"#e6eefc"}}>
      <Sidebar status={status} />
      <div style={{padding:"24px",flex:"1"}}>
        <h1 style={{marginTop:0}}>TriSLA Dashboard v3.2.2</h1>
        <p style={{opacity:.85}}>Monitoramento e Criação de Slices (NPL/GST)</p>
        <div style={{marginTop:"10px"}}>
          <b>Prometheus:</b> <span style={{color: online(status.prometheus) ? "#7CFC00" : "#ff8080"}}>{status.prometheus}</span> &nbsp;|&nbsp;
          <b>SEM-NSMF:</b> <span style={{color: online(status.sem_nsmf) ? "#7CFC00" : "#ff8080"}}>{status.sem_nsmf}</span>
        </div>
        <div style={{marginTop:"18px"}}>
          <button disabled={!online(status.sem_nsmf)} style={btnStyle(online(status.sem_nsmf))}>Criar Slice (NPL)</button>
          <button disabled={!online(status.sem_nsmf)} style={btnStyle(online(status.sem_nsmf))}>Criar Slice (GST)</button>
          <button disabled={!online(status.prometheus)} style={btnStyle(online(status.prometheus))}>Ver Métricas</button>
        </div>
      </div>
    </div>
  );
}

function btnStyle(enabled){ 
  return {
    padding:"10px 14px",
    borderRadius:"10px",
    border:"1px solid #1e3a8a",
    background: enabled ? "#122b5c" : "#0a1f47",
    color:"#e6eefc",
    cursor: enabled ? "pointer" : "not-allowed",
    marginRight:"10px"
  };
}

createRoot(document.getElementById("root")).render(<App />);

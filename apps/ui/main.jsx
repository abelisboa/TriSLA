import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";

function App() {
  const [desc, setDesc] = useState("");
  const [result, setResult] = useState(null);
  const API_BASE = "http://localhost:8000/api/v1";

  const handleSubmit = async () => {
    const res = await axios.post(`${API_BASE}/semantic`, { descricao: desc });
    setResult(res.data);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h2>TriSLA Portal – 5G/O-RAN SLA-aware</h2>
      <textarea
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        placeholder="Digite sua solicitação (ex: cirurgia remota 5G)"
        style={{ width: "100%", height: "80px" }}
      />
      <br />
      <button onClick={handleSubmit} style={{ marginTop: "10px" }}>Interpretar</button>
      {result && (
        <div style={{ marginTop: "15px" }}>
          <h4>Resultado:</h4>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

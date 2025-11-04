import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ textAlign: "center", marginTop: "10%" }}>
      <h1>TriSLA Portal</h1>
      <p>Interface de gerenciamento de SLAs em redes 5G/O-RAN</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

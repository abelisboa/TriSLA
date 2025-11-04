import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";

function Dashboard() {
  return (
    <div className='p-6 text-gray-800'>
      <h1 className='text-2xl font-bold mb-4'>TriSLA Dashboard v3.2.3</h1>
      <p>Interface unificada para Prometheus + SEM-NSMF</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className='flex'>
        <Sidebar />
        <Routes>
          <Route path='/' element={<Dashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")).render(<App />);

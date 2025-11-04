import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CreateSliceNLP from './pages/CreateSliceNLP';
import CreateSliceNEST from './pages/CreateSliceNEST';
import Monitoring from './pages/Monitoring';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-600 text-white p-4">
          <div className="container mx-auto flex space-x-4">
            <Link to="/" className="hover:text-blue-200">Dashboard</Link>
            <Link to="/create-slice-nlp" className="hover:text-blue-200">Create Slice NLP</Link>
            <Link to="/create-slice-nest" className="hover:text-blue-200">Create Slice NEST</Link>
            <Link to="/monitoring" className="hover:text-blue-200">Monitoring</Link>
          </div>
        </nav>
        <main className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create-slice-nlp" element={<CreateSliceNLP />} />
            <Route path="/create-slice-nest" element={<CreateSliceNEST />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

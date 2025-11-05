import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import CreateSliceNLP from "./pages/CreateSliceNLP"
import CreateSliceNEST from "./pages/CreateSliceNEST"
import Monitoring from "./pages/Monitoring"
import Admin from "./pages/Admin"

export default function App() {
  return (
    <BrowserRouter>
      <nav className="p-4 space-x-4 border-b">
        <Link to="/">Dashboard</Link>
        <Link to="/create-slice-nlp">Create Slice NLP</Link>
        <Link to="/create-slice-nest">Create Slice NEST</Link>
        <Link to="/monitoring">Monitoring</Link>
        <Link to="/admin">Admin</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/create-slice-nlp" element={<CreateSliceNLP />} />
        <Route path="/create-slice-nest" element={<CreateSliceNEST />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </BrowserRouter>
  )
}

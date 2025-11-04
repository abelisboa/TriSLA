import { useState } from "react"

export default function CreateSliceNEST() {
  const [template, setTemplate] = useState("{}")
  const [result, setResult] = useState(null)

  const handleSubmit = async e => {
    e.preventDefault()
    const res = await fetch("http://localhost:8000/api/v1/slices/nest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: template,
    })
    const data = await res.json()
    setResult(data)
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Create Slice (NEST Template)</h1>
      <textarea
        rows="10"
        cols="80"
        value={template}
        onChange={e => setTemplate(e.target.value)}
        className="border p-2 font-mono"
      />
      <button onClick={handleSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
        Submit NEST
      </button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}

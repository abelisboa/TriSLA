import { useState } from "react"

export default function CreateSliceNLP() {
  const [descricao, setDescricao] = useState("")
  const [result, setResult] = useState(null)

  const handleSubmit = async e => {
    e.preventDefault()
    const res = await fetch("http://localhost:8000/api/v1/slices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ descricao }),
    })
    const data = await res.json()
    setResult(data)
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">Create Slice (NLP)</h1>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          placeholder="Describe your service (e.g. remote surgery 5G)"
          className="border p-2 w-1/2"
          value={descricao}
          onChange={e => setDescricao(e.target.value)}
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>
      </form>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}

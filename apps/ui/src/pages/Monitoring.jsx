import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts"

export default function Monitoring() {
  const [data, setData] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [mode, setMode] = useState("Detecting...")

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://localhost:8000/hibrido/metrics")
      const json = await res.json()
      if (json.status === "success") {
        const now = new Date().toLocaleTimeString()
        setMode(json.mode)
        setData(prev => [...prev.slice(-20), { time: now, ...json.metrics }])
      }
    } catch (err) {
      console.error("Failed to fetch metrics:", err)
    }
  }

  useEffect(() => {
    let interval
    if (streaming) interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [streaming])

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">TriSLA Portal — Híbrido Metrics ({mode})</h2>
      <div className="flex space-x-2">
        <button onClick={() => setStreaming(true)} className="bg-green-500 text-white px-4 py-2 rounded">Start Stream</button>
        <button onClick={() => setStreaming(false)} className="bg-red-500 text-white px-4 py-2 rounded">Stop Stream</button>
      </div>
      <Card className="mt-4">
        <LineChart width={900} height={320} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="latency_ms" stroke="#8884d8" name="Latency (ms)" />
          <Line type="monotone" dataKey="jitter_ms" stroke="#82ca9d" name="Jitter (ms)" />
          <Line type="monotone" dataKey="packet_loss" stroke="#ff7300" name="Packet Loss (%)" />
          <Line type="monotone" dataKey="availability" stroke="#2f9e44" name="Availability (%)" />
        </LineChart>
      </Card>
    </div>
  )
}

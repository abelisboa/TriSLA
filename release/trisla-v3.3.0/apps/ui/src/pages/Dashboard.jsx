import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts"

const data = [
  { name: "URLLC", latency: 3.2, users: 50 },
  { name: "eMBB", latency: 12.5, users: 120 },
  { name: "mMTC", latency: 28.3, users: 1000 },
]

export default function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">TriSLA Dashboard</h1>
      <Card className="p-4">
        <BarChart width={500} height={250} data={data}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="latency" fill="#60a5fa" />
        </BarChart>
      </Card>
    </div>
  )
}

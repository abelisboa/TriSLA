import React,{useEffect,useState} from 'react'
import MainLayout from '../layout/MainLayout'
import MetricCard from '../components/MetricCard'
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer} from 'recharts'
const API=import.meta.env.VITE_API_URL||'http://localhost:5000'
export default function Dashboard(){const [prom,setProm]=useState<'ok'|'error'|'unknown'>('unknown');const [cpu,setCpu]=useState<number|null>(null);const [mem,setMem]=useState<number|null>(null);const [series,setSeries]=useState<{time:number,value:number}[]>([]);
useEffect(()=>{(async()=>{try{const r=await fetch(`${API}/api/prometheus/health`);const d=await r.json();setProm(d.status==='ok'?'ok':'error');}catch{setProm('error')}
try{const r=await fetch(`${API}/api/prometheus/metrics/system`);const d=await r.json();setCpu(d.cpu_avg??null);setMem(d.memory_mb??null);}catch{}
try{const r=await fetch(`${API}/api/prometheus/metrics/timeseries?metric=process_cpu_seconds_total`);const d=await r.json();const arr=d.data?.result?.[0]?.values??[];setSeries(arr.map((v:any)=>({time:v[0]*1000,value:parseFloat(v[1])})));}catch{setSeries([])}})()},[])
return(<MainLayout>
  <section id="dashboard">
    <div className="bg-white rounded-xl shadow-soft p-4 mb-6">{prom==='ok'?<div className="text-green-700">🟢 Prometheus online</div>:prom==='error'?<div className="text-amber-700">⚠️ Prometheus não acessível.</div>:<div className="text-gray-600">Verificando Prometheus…</div>}</div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <MetricCard title="Slices Ativos" value={0} icon={<span>🧩</span>}/>
      <MetricCard title="Componentes UP" value={0} icon={<span>🧱</span>}/>
      <MetricCard title="CPU Médio" value={cpu==null?null:(cpu).toFixed(2)} suffix="%" icon={<span>💻</span>}/>
      <MetricCard title="Memória (MB)" value={mem==null?null:mem.toFixed(0)} icon={<span>💾</span>}/>
    </div>
    <div id="metrics" className="bg-white rounded-xl shadow-soft p-6 mt-6">
      <div className="text-sm text-gray-500 mb-2">CPU (últimos 5 min)</div>
      {series.length===0?<div className="rounded-md border p-4 text-gray-600">Sem dados de séries temporais.</div>:
        <div style={{width:'100%',height:300}}><ResponsiveContainer><LineChart data={series}>
          <XAxis dataKey="time" tickFormatter={(t)=>new Date(t).toLocaleTimeString()}/><YAxis/><Tooltip labelFormatter={(t)=>new Date(t as number).toLocaleTimeString()}/><Line type="monotone" dataKey="value" dot={false}/>
        </LineChart></ResponsiveContainer></div>}
    </div>
  </section>
</MainLayout>)}

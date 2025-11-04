import React,{useEffect,useState} from 'react'
import MainLayout from '../../layout/MainLayout'
const API=import.meta.env.VITE_API_URL||'http://localhost:5000'
export default function SlicesIndex(){const [items,setItems]=useState<any[]>([]);useEffect(()=>{fetch(`${API}/api/slices/list`).then(r=>r.json()).then(d=>setItems(d.items||[])).catch(()=>setItems([]))},[])
return(<MainLayout>
  <section id="slices"><h2 className="text-xl font-semibold mb-4">Slices</h2>
    <div className="bg-white rounded-xl shadow-soft p-4">{items.length===0?<div className="text-gray-600">Nenhum slice criado ainda.</div>:
      <div className="overflow-auto"><table className="min-w-full text-sm"><thead className="text-left text-gray-500"><tr><th className="p-2">ID</th><th className="p-2">Origem</th><th className="p-2">Tipo</th><th className="p-2">Nome</th><th className="p-2">Status</th><th className="p-2">Criado em</th></tr></thead>
      <tbody>{items.map((it:any)=>(<tr key={it.id} className="border-t"><td className="p-2">{it.id}</td><td className="p-2">{it.source}</td><td className="p-2">{it.nest?.type}</td><td className="p-2">{it.nest?.name}</td><td className="p-2">{it.status}</td><td className="p-2">{it.created_at}</td></tr>))}</tbody></table></div>}
    </div>
  </section>
</MainLayout>)}

import React,{useState} from 'react';const API=import.meta.env.VITE_API_URL||'http://localhost:5000'
export default function SlicePromptNPL(){const [prompt,setPrompt]=useState('Necessito de slice para cirurgia remota com baixa latência.');const [resp,setResp]=useState<any>(null);const [loading,setLoading]=useState(false);
const handle=async()=>{setLoading(true);try{const r=await fetch(`${API}/api/slices/nlp/create`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});const d=await r.json();setResp(d);}finally{setLoading(false);}}
return(<div className="bg-white rounded-xl shadow-soft p-6">
  <div className="mb-2 text-sm text-gray-600">Digite a intenção em linguagem natural:</div>
  <textarea className="w-full border rounded-lg p-3" rows={4} value={prompt} onChange={e=>setPrompt(e.target.value)}/>
  <div className="mt-3 flex gap-2"><button onClick={handle} className="px-4 py-2 rounded-lg bg-sidebar text-white">{loading?'Gerando...':'Gerar Template'}</button></div>
  {resp&&(<pre className="mt-4 bg-gray-50 p-3 rounded-lg overflow-auto text-sm">{JSON.stringify(resp,null,2)}</pre>)}
</div>)}

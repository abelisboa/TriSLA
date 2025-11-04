export default function Sidebar({ status }) {
  const item = (label, enabled=true) => (
    <div style={{padding:"10px 12px", borderRadius:"10px", margin:"6px 0", opacity: enabled ? 1 : 0.4, background:"#0e2248", border:"1px solid #1e3a8a"}}>
      {label}
    </div>
  );
  const badge = (name, ok) => (
    <div style={{display:"flex", justifyContent:"space-between", fontSize:"12px", marginTop:"4px"}}>
      <span>{name}</span>
      <span style={{color: ok ? "#7CFC00" : "#ff8080"}}>{ok ? "online" : "offline"}</span>
    </div>
  );
  return (
    <div style={{width:"260px", padding:"20px", background:"#0a1a38", borderRight:"1px solid #102a5c"}}>
      <div style={{fontWeight:700, fontSize:"18px", marginBottom:"12px"}}>TriSLA</div>
      {item("Criar Slice (NPL)", status.sem_nsmf==="online")}
      {item("Criar Slice (GST)", status.sem_nsmf==="online")}
      {item("Métricas", status.prometheus==="online")}
      <div style={{marginTop:"14px", paddingTop:"10px", borderTop:"1px dashed #1f3466"}}>
        <div style={{fontWeight:600, marginBottom:"6px"}}>Módulos</div>
        {badge("Prometheus", status.prometheus==="online")}
        {badge("SEM-NSMF", status.sem_nsmf==="online")}
      </div>
    </div>
  );
}
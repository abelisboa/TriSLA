export default function Slices({ enabledNPL, enabledGST, metricsEnabled }) {
  const btn = (label, enabled=true) => (
    <button disabled={!enabled} style={{padding:"10px 14px", borderRadius:"10px", border:"1px solid #1e3a8a", background: enabled ? "#122b5c" : "#0a1f47", color:"#e6eefc", cursor: enabled ? "pointer" : "not-allowed", marginRight:"10px"}}>
      {label}
    </button>
  );
  return (
    <div>
      <h2 style={{marginTop:0}}>Slices</h2>
      <div style={{marginBottom:"16px"}}>
        {btn("Criar Slice (NPL)", enabledNPL)}
        {btn("Criar Slice (GST)", enabledGST)}
        {btn("Ver métricas", metricsEnabled)}
      </div>
      <p>As opções são liberadas automaticamente quando os módulos necessários estiverem online.</p>
    </div>
  );
}
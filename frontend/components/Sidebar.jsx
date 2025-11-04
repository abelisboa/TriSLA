import React, { useEffect, useState } from "react";

export default function Sidebar() {
  const [status, setStatus] = useState({ prometheus: false, sem: false });

  async function fetchStatus() {
    try {
      const res = await fetch("http://localhost:5000/api/status");
      const data = await res.json();
      setStatus({
        prometheus: data.prometheus_online,
        sem: data.sem_nsmf_online,
      });
    } catch {
      setStatus({ prometheus: false, sem: false });
    }
  }

  useEffect(() => {
    fetchStatus();
    const id = setInterval(fetchStatus, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <aside className="w-64 p-4 bg-slate-900 text-white h-screen">
      <h1 className="text-lg font-bold mb-4">TriSLA Dashboard</h1>
      <nav className="flex flex-col space-y-2">
        <a href="/" className="hover:text-blue-400">Overview</a>
        <a href="/metrics" className="hover:text-blue-400">Metrics</a>
        <a href="/slices-npl" className="hover:text-blue-400">Create Slice (NPL)</a>
        <a href="/slices-gst" className="hover:text-blue-400">Create Slice (GST)</a>
      </nav>

      <div className="mt-6 text-sm">
        <div>
          Prometheus:{" "}
          <span className={status.prometheus ? "text-green-400" : "text-red-400"}>
            {status.prometheus ? "online" : "offline"}
          </span>
        </div>
        <div>
          SEM-NSMF:{" "}
          <span className={status.sem ? "text-green-400" : "text-red-400"}>
            {status.sem ? "online" : "offline"}
          </span>
        </div>
      </div>
    </aside>
  );
}

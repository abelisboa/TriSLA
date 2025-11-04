import React from 'react'
export default function MainLayout({ children }:{children:React.ReactNode}){
  return (<div className="min-h-screen flex bg-gray-50">
    <aside className="w-64 bg-sidebar text-white p-6 hidden md:block">
      <div className="text-2xl font-bold mb-6">TriSLA</div>
      <nav className="space-y-3">
        <a className="block hover:underline" href="#dashboard">📊 Dashboard</a>
        <div className="text-sm uppercase text-white/70 mt-4 mb-2">Slices</div>
        <a className="block hover:underline" href="#slices">🧩 Lista</a>
        <a className="block hover:underline" href="#slices-npl">💬 Criar Slice (NPL)</a>
        <a className="block hover:underline" href="#slices-gst">🧮 Criar Slice (GST)</a>
        <div className="text-sm uppercase text-white/70 mt-4 mb-2">Operação</div>
        <a className="block hover:underline" href="#metrics">📈 Métricas</a>
        <a className="block hover:underline" href="#templates">🧠 Templates</a>
        <a className="block hover:underline" href="#admin">🧑‍💻 Admin</a>
      </nav>
    </aside>
    <main className="flex-1 p-4 md:p-8">{children}</main>
  </div>)
}
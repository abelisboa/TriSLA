import React from 'react'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-6">
          <h1 className="text-2xl font-bold text-brand-800">TriSLA</h1>
          <nav className="text-sm">
            <a className="mr-4" href="#">Dashboard</a>
            <a className="mr-4" href="#slices">Slices</a>
            <a href="#metrics">Métricas</a>
          </nav>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid gap-6">{children}</div>
      </main>
    </div>
  )
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  Home,
  FileText,
  Settings,
  BarChart3,
  Activity,
} from 'lucide-react'

// Menu conforme arquitetura TriSLA
const navigation = [
  { name: 'HOME', href: '/', icon: Home },
  { name: 'Criar SLA (PNL)', href: '/slas/create/pln', icon: FileText },
  { name: 'Criar SLA (Template)', href: '/slas/create/template', icon: Settings },
  { name: 'Monitoramento', href: '/slas/monitoring', icon: BarChart3 },
  { name: 'Métricas', href: '/slas/metrics', icon: Activity },
  { name: 'Administração', href: '/modules', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col bg-card border-r">
      <div className="flex h-16 items-center border-b px-6">
        <Activity className="h-6 w-6 text-primary mr-2" />
        <h1 className="text-sm font-bold leading-tight">TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname?.startsWith(item.href))
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

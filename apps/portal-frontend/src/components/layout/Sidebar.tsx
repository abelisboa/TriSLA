"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type MenuItem = {
  href: string;
  label: string;
};

type MenuSection = {
  id: string;
  title: string;
  items: MenuItem[];
};

/** Menus agrupados por domínio científico, mantendo as rotas atuais. */
const SECTIONS: MenuSection[] = [
  {
    id: "lifecycle",
    title: "SLA Lifecycle",
    items: [
      { href: "/sla-lifecycle", label: "SLA Lifecycle" },
    ],
  },
  {
    id: "creation",
    title: "SLA Creation",
    items: [
      { href: "/pnl", label: "Criar SLA PNL" },
      { href: "/template", label: "Criar SLA Template" },
    ],
  },
  {
    id: "observability",
    title: "Observability",
    items: [
      { href: "/monitoring", label: "Monitoring & Metrics" },
    ],
  },
  {
    id: "governance",
    title: "Administration",
    items: [
      { href: "/administration", label: "Administration" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="trisla-sidebar">
      <div className="trisla-sidebar-header">
        <span className="trisla-logo">TriSLA</span>
        <span className="trisla-logo-subtitle">SLA-Centric Scientific Portal</span>
      </div>
      <nav className="trisla-sidebar-nav" aria-label="TriSLA scientific navigation">
        {SECTIONS.map((section, index) => (
          <div key={section.id} className="trisla-sidebar-section">
            <div className="trisla-sidebar-section-title">{section.title}</div>
            <ul>
              {section.items.map((item) => {
                const active =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname?.startsWith(item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={
                        active ? "trisla-nav-link active" : "trisla-nav-link"
                      }
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
            {index < SECTIONS.length - 1 ? (
              <div className="trisla-sidebar-divider" />
            ) : null}
          </div>
        ))}
      </nav>
    </aside>
  );
}

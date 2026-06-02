"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { isRuntimeLifecycleNavVisible } from "../../lib/lifecycleViewFilter";
import { usePortalNavContext } from "../../lib/portalNavContext";

type MenuItem = {
  href: string;
  label: string;
  /** When true, hidden unless runtime lifecycle nav is allowed for current decision. */
  runtimeGated?: boolean;
  /** Match ?view= query on /sla-lifecycle for active state. */
  lifecycleView?: "admission" | "runtime";
};

type MenuSection = {
  id: string;
  title: string;
  items: MenuItem[];
};

/** Sprint 10F — consolidated operational navigation (SAFE). */
const SECTIONS: MenuSection[] = [
  {
    id: "overview",
    title: "Platform Overview",
    items: [{ href: "/", label: "Platform Overview" }],
  },
  {
    id: "creation",
    title: "SLA Creation",
    items: [
      { href: "/pnl", label: "Natural Language SLA" },
      { href: "/template", label: "Structured SLA" },
    ],
  },
  {
    id: "admission",
    title: "Admission Analysis",
    items: [
      {
        href: "/sla-lifecycle?view=admission",
        label: "Admission Analysis",
        lifecycleView: "admission",
      },
    ],
  },
  {
    id: "runtime",
    title: "Runtime Lifecycle",
    items: [
      {
        href: "/sla-lifecycle?view=runtime",
        label: "Runtime Lifecycle",
        runtimeGated: true,
        lifecycleView: "runtime",
      },
    ],
  },
  {
    id: "analytics",
    title: "Domain Analytics",
    items: [{ href: "/monitoring", label: "Domain Analytics" }],
  },
];

function isActive(pathname: string | null, view: string | null, item: MenuItem): boolean {
  if (item.lifecycleView) {
    return pathname === "/sla-lifecycle" && view === item.lifecycleView;
  }
  if (item.href === "/") return pathname === "/";
  const base = item.href.split("?")[0];
  return Boolean(pathname?.startsWith(base));
}

export function Sidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const view = searchParams.get("view");
  const { admissionDecision } = usePortalNavContext();
  const showRuntimeNav = isRuntimeLifecycleNavVisible(admissionDecision);

  return (
    <aside className="trisla-sidebar">
      <div className="trisla-sidebar-header">
        <span className="trisla-logo">TriSLA</span>
        <span className="trisla-logo-subtitle">SLA Management Platform</span>
      </div>
      <nav className="trisla-sidebar-nav" aria-label="TriSLA operational navigation">
        {SECTIONS.map((section, index) => {
          const visibleItems = section.items.filter(
            (item) => !item.runtimeGated || showRuntimeNav,
          );
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.id} className="trisla-sidebar-section">
              <div className="trisla-sidebar-section-title">{section.title}</div>
              <ul>
                {visibleItems.map((item) => {
                  const active = isActive(pathname, view, item);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={active ? "trisla-nav-link active" : "trisla-nav-link"}
                      >
                        {item.label}
                      </Link>
                    </li>
                  );
                })}
              </ul>
              {index < SECTIONS.length - 1 ? <div className="trisla-sidebar-divider" /> : null}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}

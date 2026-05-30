import type { ReactNode } from "react";

type Props = {
  id: string;
  level: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  children: ReactNode;
};

export function DashboardSection({ id, level, children }: Props) {
  return (
    <div id={id} className={`trisla-dashboard-section trisla-level-${level}`}>
      {children}
    </div>
  );
}

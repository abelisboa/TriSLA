"use client";

import React from "react";
import "./globals.css";
import { Sidebar } from "../components/layout/Sidebar";
import { Topbar } from "../components/layout/Topbar";
import { PageContainer } from "../components/layout/PageContainer";
import { PortalNavProvider } from "../lib/portalNavContext";
import { Suspense } from "react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-US">
      <body className="trisla-body">
        <PortalNavProvider>
          <div className="trisla-shell">
            <Suspense fallback={null}>
              <Sidebar />
            </Suspense>
            <div className="trisla-main">
              <Topbar />
              <PageContainer>{children}</PageContainer>
            </div>
          </div>
        </PortalNavProvider>
      </body>
    </html>
  );
}

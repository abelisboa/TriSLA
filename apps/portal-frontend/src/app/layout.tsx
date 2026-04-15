"use client";

import React from "react";
import "./globals.css";
import { Sidebar } from "../components/layout/Sidebar";
import { Topbar } from "../components/layout/Topbar";
import { PageContainer } from "../components/layout/PageContainer";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="trisla-body">
        <div className="trisla-shell">
          <Sidebar />
          <div className="trisla-main">
            <Topbar />
            <PageContainer>{children}</PageContainer>
          </div>
        </div>
      </body>
    </html>
  );
}

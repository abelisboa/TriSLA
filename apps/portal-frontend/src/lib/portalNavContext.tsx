"use client";

import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { AdmissionDecision } from "./admissionLifecycleGate";

type PortalNavContextValue = {
  intentId: string | null;
  admissionDecision: AdmissionDecision | null;
  setPortalNavContext: (update: {
    intentId?: string | null;
    admissionDecision?: AdmissionDecision | null;
  }) => void;
  clearPortalNavContext: () => void;
};

const PortalNavContext = createContext<PortalNavContextValue | null>(null);

export function PortalNavProvider({ children }: { children: React.ReactNode }) {
  const [intentId, setIntentId] = useState<string | null>(null);
  const [admissionDecision, setAdmissionDecision] = useState<AdmissionDecision | null>(null);

  const setPortalNavContext = useCallback(
    (update: { intentId?: string | null; admissionDecision?: AdmissionDecision | null }) => {
      if ("intentId" in update) setIntentId(update.intentId ?? null);
      if ("admissionDecision" in update) setAdmissionDecision(update.admissionDecision ?? null);
    },
    [],
  );

  const clearPortalNavContext = useCallback(() => {
    setIntentId(null);
    setAdmissionDecision(null);
  }, []);

  const value = useMemo(
    () => ({ intentId, admissionDecision, setPortalNavContext, clearPortalNavContext }),
    [intentId, admissionDecision, setPortalNavContext, clearPortalNavContext],
  );

  return <PortalNavContext.Provider value={value}>{children}</PortalNavContext.Provider>;
}

export function usePortalNavContext(): PortalNavContextValue {
  const ctx = useContext(PortalNavContext);
  if (!ctx) {
    throw new Error("usePortalNavContext must be used within PortalNavProvider");
  }
  return ctx;
}

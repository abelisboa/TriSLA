"use client";

import { useCallback, useState } from "react";

type Props = {
  value: string;
  className?: string;
};

export function CopyableHash({ value, className }: Props) {
  const [copied, setCopied] = useState(false);

  const onCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  }, [value]);

  return (
    <span className={className}>
      <code className="trisla-hash-inline">{value}</code>{" "}
      <button type="button" className="trisla-copy-btn" onClick={onCopy} title="Copy full hash">
        {copied ? "Copied" : "Copy"}
      </button>
    </span>
  );
}

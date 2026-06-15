type DataStateProps = {
  status: "idle" | "loading" | "ready" | "error";
  errorMessage?: string;
  children?: React.ReactNode;
};

export function DataState({ status, errorMessage, children }: DataStateProps) {
  if (status === "loading") {
    return <p>Loading live data from TriSLA backend…</p>;
  }

  if (status === "error") {
    return (
      <p>
        Source unavailable: <span>{errorMessage ?? "error retrieving source data"}</span>
      </p>
    );
  }

  if (status === "idle") {
    return null;
  }

  return <>{children}</>;
}


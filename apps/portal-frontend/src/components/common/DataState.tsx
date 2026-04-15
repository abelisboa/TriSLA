type DataStateProps = {
  status: "idle" | "loading" | "ready" | "error";
  errorMessage?: string;
  children?: React.ReactNode;
};

export function DataState({ status, errorMessage, children }: DataStateProps) {
  if (status === "loading") {
    return <p>Carregando dados reais do backend TriSLA…</p>;
  }

  if (status === "error") {
    return (
      <p>
        Fonte indisponível: <span>{errorMessage ?? "erro ao consultar fonte real"}</span>
      </p>
    );
  }

  if (status === "idle") {
    return null;
  }

  return <>{children}</>;
}


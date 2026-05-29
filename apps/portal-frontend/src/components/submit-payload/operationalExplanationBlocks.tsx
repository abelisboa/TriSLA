import { displayField } from "../../lib/submitResponse";

type Props = {
  title: string;
  headers: string[];
  rows: string[][];
};

export function SimpleTable({ title, headers, rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className="trisla-op-section">
        <h3>{title}</h3>
        <p className="trisla-muted">Not available</p>
      </div>
    );
  }

  return (
    <div className="trisla-op-section">
      <h3>{title}</h3>
      <div className="trisla-table-wrap">
        <table className="trisla-simple-table">
          <thead>
            <tr>
              {headers.map((h) => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function TextBlock({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="trisla-op-section">
      <h3>{title}</h3>
      <p className="trisla-op-text">{displayField(value)}</p>
    </div>
  );
}

export function ReasonCodesBlock({ codes }: { codes: unknown }) {
  const list = Array.isArray(codes) ? codes : codes === null || codes === undefined ? [] : [codes];

  return (
    <div className="trisla-op-section">
      <h3>Decision Reasons</h3>
      {list.length === 0 ? (
        <p className="trisla-muted">Not available</p>
      ) : (
        <ul className="trisla-reason-codes">
          {list.map((code, i) => (
            <li key={`${String(code)}-${i}`}>
              <code>{String(code)}</code>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function contributingFactorRows(factors: unknown): { headers: string[]; rows: string[][] } {
  if (!Array.isArray(factors) || factors.length === 0) {
    return { headers: [], rows: [] };
  }
  const objects = factors.filter((f) => f && typeof f === "object" && !Array.isArray(f)) as Record<
    string,
    unknown
  >[];
  if (objects.length === 0) {
    return { headers: [], rows: [] };
  }
  const headers = Object.keys(objects[0]);
  const rows = objects.map((obj) => headers.map((h) => displayField(obj[h])));
  return { headers, rows };
}

export function thresholdRows(thresholds: unknown): { headers: string[]; rows: string[][] } {
  if (!thresholds || typeof thresholds !== "object" || Array.isArray(thresholds)) {
    return { headers: [], rows: [] };
  }
  const entries = Object.entries(thresholds as Record<string, unknown>);
  if (entries.length === 0) {
    return { headers: [], rows: [] };
  }
  return {
    headers: ["Threshold", "Value"],
    rows: entries.map(([k, v]) => [k, displayField(v)]),
  };
}

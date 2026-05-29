import { displayField } from "../../lib/submitResponse";

export type FieldEntry = {
  label: string;
  value: unknown;
};

export function FieldList({ fields }: { fields: FieldEntry[] }) {
  return (
    <dl>
      {fields.map(({ label, value }) => (
        <div key={label} className="trisla-status-row">
          <dt>{label}</dt>
          <dd className={typeof value === "object" && value !== null ? "trisla-pre-wrap" : undefined}>
            {displayField(value)}
          </dd>
        </div>
      ))}
    </dl>
  );
}

import { displayField } from "../../lib/submitResponse";

export type FieldEntry = {
  label: string;
  value: unknown;
  title?: string;
};

export function FieldList({ fields }: { fields: FieldEntry[] }) {
  return (
    <dl>
      {fields.map(({ label, value, title }) => (
        <div key={label} className="trisla-status-row">
          <dt title={title}>{label}</dt>
          <dd className={typeof value === "object" && value !== null ? "trisla-pre-wrap" : undefined}>
            {displayField(value)}
          </dd>
        </div>
      ))}
    </dl>
  );
}

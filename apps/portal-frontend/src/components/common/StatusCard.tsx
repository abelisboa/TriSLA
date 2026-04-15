type StatusCardProps = {
  title: string;
  items: { label: string; value: string }[];
};

export function StatusCard({ title, items }: StatusCardProps) {
  return (
    <section className="trisla-status-card">
      <h2>{title}</h2>
      <dl>
        {items.map((item) => (
          <div key={item.label} className="trisla-status-row">
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}


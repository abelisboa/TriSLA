export function Card({ children, className = "" }) {
  return (
    <div className={`rounded-xl border bg-white shadow-sm p-4 ${className}`}>
      {children}
    </div>
  )
}

export function Input({ className = "", ...props }) {
  return (
    <input
      className={`border p-2 rounded w-full focus:ring focus:ring-blue-300 ${className}`}
      {...props}
    />
  )
}

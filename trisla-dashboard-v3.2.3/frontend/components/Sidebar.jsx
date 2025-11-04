export default function Sidebar() {
  return (
    <aside className='w-60 bg-white shadow h-screen p-4'>
      <h2 className='font-bold text-lg mb-4'>TriSLA Menu</h2>
      <ul className='space-y-2 text-gray-700'>
        <li><a href='/'>Dashboard</a></li>
      </ul>
    </aside>
  );
}
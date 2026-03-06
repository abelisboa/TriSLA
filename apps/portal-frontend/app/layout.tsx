export const metadata = {
  title: 'TriSLA Portal',
  description: 'TriSLA Observability Portal',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

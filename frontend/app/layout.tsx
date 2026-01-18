import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Syllabus to Quiz',
  description: 'Convert syllabus images into adaptive quiz modules',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}

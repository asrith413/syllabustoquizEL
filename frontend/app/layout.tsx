import type { Metadata } from 'next'
import { Inter, Outfit } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'

const outfit = Outfit({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SocratAI - Master Your Syllabus',
  description: 'AI-powered adaptive learning platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={outfit.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ComptaOHADA-IA | Plateforme de Comptabilité OHADA avec IA',
  description: 'Plateforme de comptabilité en ligne pour les entités à but non lucratif de l\'espace OHADA avec intelligence artificielle intégrée selon les normes SYSCEBNL.',
  keywords: ['comptabilité', 'OHADA', 'SYSCEBNL', 'EBNL', 'intelligence artificielle', 'Next.js', 'FastAPI'],
  authors: [{ name: 'ComptaOHADA-IA Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'ComptaOHADA-IA | Plateforme de Comptabilité OHADA avec IA',
    description: 'Plateforme de comptabilité en ligne pour les entités à but non lucratif de l\'espace OHADA',
    type: 'website',
    locale: 'fr_FR',
    siteName: 'ComptaOHADA-IA',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ComptaOHADA-IA | Plateforme de Comptabilité OHADA avec IA',
    description: 'Plateforme de comptabilité en ligne pour les entités à but non lucratif de l\'espace OHADA',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 antialiased`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                style: {
                  background: '#22c55e',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
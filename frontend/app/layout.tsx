import { Outfit, Inter } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-heading",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Lupa Política | Transparência Legislativa",
  description: "Análise inteligente de gastos e proposições da Câmara dos Deputados.",
};

import { Navbar } from "@/components/Navbar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body
        className={`${outfit.variable} ${inter.variable} font-body bg-background text-foreground antialiased`}
      >
        <div className="relative min-h-screen">
          <Navbar />
          {/* Dashboard Gradient Background */}
          <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_-20%,#00A85915,transparent_50%)] pointer-events-none" />
          <div className="relative z-10 pt-24 pb-12 px-6 max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}

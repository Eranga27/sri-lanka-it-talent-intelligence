import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sri Lanka IT Talent Intelligence",
  description:
    "Data-driven intelligence on IT industry demand and talent supply in Sri Lanka. " +
    "Track live vacancies, role demand, skill gaps, and workforce trends.",
  keywords: ["Sri Lanka", "IT jobs", "tech talent", "workforce", "data analytics"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

function Header() {
  return (
    <header className="sticky top-0 z-50 glass border-b border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
            <span className="text-blue-400 text-xs font-bold">LK</span>
          </div>
          <span className="text-sm font-semibold text-white tracking-tight">
            Sri Lanka{" "}
            <span className="text-blue-400 font-light">IT Intelligence</span>
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-6" aria-label="Main navigation">
          <a href="#market" className="text-xs font-medium text-gray-400 hover:text-white transition-colors duration-150">
            Market
          </a>
          <a href="#roles" className="text-xs font-medium text-gray-400 hover:text-white transition-colors duration-150">
            Roles
          </a>
          <a href="#sources" className="text-xs font-medium text-gray-400 hover:text-white transition-colors duration-150">
            Sources
          </a>
          <a href="#methodology" className="text-xs font-medium text-gray-400 hover:text-white transition-colors duration-150">
            Methodology
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-semibold badge-live tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            PHASE 1B
          </span>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-10 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-xs text-gray-500">
          © {new Date().getFullYear()} Sri Lanka IT Talent Intelligence.
          Zero-cost. Data-driven.
        </p>
        <p className="text-xs text-gray-600">
          All analytical values computed from live source data. No figures are hardcoded.
        </p>
      </div>
    </footer>
  );
}

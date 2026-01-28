"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, Info, LayoutDashboard, Users, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Deputados", href: "/deputados", icon: Users },
  { name: "Proposições", href: "/proposicoes", icon: FileText },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
      <div className="glass w-full max-w-4xl px-3 sm:px-6 py-3 rounded-full flex items-center gap-2 sm:gap-6 shadow-2xl shadow-emerald-500/10 overflow-visible box-border">
        {/* Left fixed: logo icon only */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:rotate-12 transition-transform duration-300">
              <Search className="w-5 h-5 text-primary-foreground" />
            </div>
          </Link>
        </div>

        {/* Divider between fixed left and sliding nav */}
        <div className="h-6 w-px bg-border mx-3 block" />

        {/* Sliding nav (center) */}
        <div className="flex-1 min-w-0 flex items-center">
          <div className="min-w-0 flex items-center gap-2 flex-nowrap overflow-x-auto md:overflow-visible">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 whitespace-nowrap",
                  pathname === item.href
                    ? "bg-primary/20 text-primary shadow-[inset_0_0_10px_rgba(0,168,89,0.1)]"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                )}
              >
                <item.icon className="w-4 h-4" />
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        {/* Divider between sliding nav and fixed right */}
        <div className="h-6 w-px bg-border mx-3 block" />

        {/* Right fixed: Sobre link */}
        <div className="ml-2 flex items-center flex-shrink-0">
          <Link href="/about" className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors duration-200">
            <Info className="w-4 h-4" />
            <span className="text-xs uppercase tracking-widest font-bold">Sobre</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}

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
    <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      <div className="glass px-6 py-3 rounded-full flex items-center gap-8 shadow-2xl shadow-emerald-500/10">
        <Link href="/" className="flex items-center gap-2 mr-4 group">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:rotate-12 transition-transform duration-300">
            <Search className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="font-heading font-bold text-lg tracking-tight">
            LUPA <span className="text-primary font-extrabold">POLÍTICA</span>
          </span>
        </Link>

        <div className="flex items-center gap-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
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

        <div className="ml-4 h-6 w-px bg-border" />

        <button className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors duration-200 ml-2">
          <Info className="w-4 h-4" />
          <span className="text-xs uppercase tracking-widest font-bold">Sobre</span>
        </button>
      </div>
    </nav>
  );
}

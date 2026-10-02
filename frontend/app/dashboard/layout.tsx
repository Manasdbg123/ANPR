"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Camera, Search, BarChart3, Bell, Bot,
  Settings, Activity, Scan, LogOut, Menu, X, ChevronLeft, User
} from "lucide-react";
import { api } from "@/lib/api";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/dashboard/cameras", icon: Camera, label: "Cameras" },
  { href: "/dashboard/detections", icon: Search, label: "Detections" },
  { href: "/dashboard/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/dashboard/alerts", icon: Bell, label: "Alerts" },
  { href: "/dashboard/assistant", icon: Bot, label: "AI Assistant" },
  { href: "/dashboard/system", icon: Activity, label: "System" },
  { href: "/dashboard/settings", icon: Settings, label: "Settings" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      router.push("/login");
      return;
    }
    api.getMe().then((res) => setUser(res.data)).catch(() => {
      router.push("/login");
    });
  }, [router]);

  const handleLogout = () => {
    api.clearToken();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-[var(--background)] flex">
      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 z-40 lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen z-50 flex flex-col border-r border-[var(--border)] bg-[var(--card)] transition-all duration-300 ${
          collapsed ? "w-16" : "w-60"
        } ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Logo */}
        <div className={`h-16 flex items-center border-b border-[var(--border)] ${collapsed ? "justify-center px-2" : "px-4 gap-2"}`}>
          <div className="w-8 h-8 rounded-lg bg-[var(--primary)] flex items-center justify-center shrink-0">
            <Scan className="w-5 h-5 text-white" />
          </div>
          {!collapsed && <span className="font-semibold text-sm tracking-tight">VisionTrack</span>}
          <button
            onClick={() => setMobileOpen(false)}
            className="lg:hidden ml-auto text-[var(--muted-foreground)] hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = pathname === item.href || (item.href !== "/dashboard" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  active
                    ? "bg-[var(--primary)]/10 text-[var(--primary)] font-medium"
                    : "text-[var(--muted-foreground)] hover:text-white hover:bg-[var(--secondary)]"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <item.icon className="w-[18px] h-[18px] shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <div className="hidden lg:block px-2 py-2 border-t border-[var(--border)]">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-[var(--muted-foreground)] hover:text-white hover:bg-[var(--secondary)] text-sm transition"
          >
            <ChevronLeft className={`w-4 h-4 transition-transform ${collapsed ? "rotate-180" : ""}`} />
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>

        {/* User */}
        <div className={`border-t border-[var(--border)] p-3 ${collapsed ? "flex justify-center" : ""}`}>
          {collapsed ? (
            <button onClick={handleLogout} className="text-[var(--muted-foreground)] hover:text-white transition">
              <LogOut className="w-4 h-4" />
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[var(--primary)]/20 flex items-center justify-center">
                <User className="w-4 h-4 text-[var(--primary)]" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.full_name || user?.username || "User"}</p>
                <p className="text-xs text-[var(--muted-foreground)] truncate capitalize">{user?.role || ""}</p>
              </div>
              <button onClick={handleLogout} className="text-[var(--muted-foreground)] hover:text-white transition">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 border-b border-[var(--border)] flex items-center justify-between px-6 bg-[var(--card)]">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden text-[var(--muted-foreground)] hover:text-white"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-sm font-medium text-[var(--muted-foreground)]">
              {navItems.find(n => pathname === n.href || (n.href !== "/dashboard" && pathname?.startsWith(n.href)))?.label || "Dashboard"}
            </h2>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--success)]/10 border border-[var(--success)]/20">
              <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)] animate-pulse" />
              <span className="text-xs text-[var(--success)]">System Online</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="p-6"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
}

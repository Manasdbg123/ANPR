"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Settings, User, Shield, Moon, Sun, Monitor } from "lucide-react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    api.getMe().then((res) => setUser(res.data)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="text-sm text-[var(--muted-foreground)]">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <User className="w-4 h-4 text-[var(--primary)]" />
          <h3 className="font-semibold">Profile</h3>
        </div>
        {user && (
          <div className="space-y-3">
            {[
              ["Username", user.username],
              ["Email", user.email],
              ["Full Name", user.full_name || "—"],
              ["Role", user.role],
              ["Status", user.is_active ? "Active" : "Inactive"],
            ].map(([label, value]) => (
              <div key={label as string} className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0">
                <span className="text-sm text-[var(--muted-foreground)]">{label}</span>
                <span className="text-sm font-medium capitalize">{value as string}</span>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Roles & Permissions */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-4 h-4 text-[var(--primary)]" />
          <h3 className="font-semibold">Roles & Permissions</h3>
        </div>
        <div className="space-y-3">
          {[
            { role: "Admin", desc: "Full system access, user management, camera configuration", color: "var(--destructive)" },
            { role: "Operator", desc: "Camera management, detection monitoring, alert management", color: "var(--warning)" },
            { role: "Viewer", desc: "Read-only access to dashboards and detection history", color: "var(--info)" },
          ].map((r) => (
            <div key={r.role} className="flex items-start gap-3 py-2">
              <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: r.color }} />
              <div>
                <p className="text-sm font-medium">{r.role}</p>
                <p className="text-xs text-[var(--muted-foreground)]">{r.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* App Info */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <Monitor className="w-4 h-4 text-[var(--primary)]" />
          <h3 className="font-semibold">Application</h3>
        </div>
        <div className="space-y-2">
          {[
            ["Application", "VisionTrack ANPR"],
            ["Version", "1.0.0"],
            ["Environment", "Development"],
            ["Demo Mode", "Enabled"],
          ].map(([k, v]) => (
            <div key={k as string} className="flex items-center justify-between py-1.5">
              <span className="text-sm text-[var(--muted-foreground)]">{k}</span>
              <span className="text-sm">{v}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

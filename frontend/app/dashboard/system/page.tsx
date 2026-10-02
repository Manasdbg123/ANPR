"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Database, Server, Cpu, Camera, Wifi, HardDrive, Clock } from "lucide-react";
import { api } from "@/lib/api";

export default function SystemPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      const res = await api.getDetailedHealth();
      setHealth(res.data);
    } catch {
      try {
        const res = await api.getSystemHealth();
        setHealth(res.data);
      } catch (err) {
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-16 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        ))}
      </div>
    );
  }

  const statusColor = (status: string) => {
    if (status === "healthy" || status === "available" || status === "loaded" || status === "running") return "var(--success)";
    if (status === "degraded" || status === "cpu_only") return "var(--warning)";
    return "var(--destructive)";
  };

  const statusIcon = (status: string) => {
    const color = statusColor(status);
    return <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />;
  };

  const services = [
    { name: "API Server", status: health?.api || "unknown", icon: Server },
    { name: "PostgreSQL", status: health?.database || "unknown", icon: Database },
    { name: "Redis", status: health?.redis || "unknown", icon: HardDrive },
    { name: "GPU", status: health?.gpu || "unknown", icon: Cpu },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">System Health</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          VisionTrack v{health?.version || "1.0.0"} • Uptime: {Math.floor((health?.uptime_seconds || 0) / 60)}m
        </p>
      </div>

      {/* Overall Status */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl border p-5 ${
          health?.status === "healthy"
            ? "border-[var(--success)]/20 bg-[var(--success)]/5"
            : "border-[var(--warning)]/20 bg-[var(--warning)]/5"
        }`}
      >
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${health?.status === "healthy" ? "bg-[var(--success)]" : "bg-[var(--warning)]"} animate-pulse`} />
          <h2 className="text-lg font-semibold capitalize">System {health?.status || "Unknown"}</h2>
        </div>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          {health?.cameras_online || 0} of {health?.cameras_total || 0} cameras online
        </p>
      </motion.div>

      {/* Services */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((svc, i) => (
          <motion.div
            key={svc.name}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-lg bg-[var(--secondary)] flex items-center justify-center">
              <svc.icon className="w-5 h-5 text-[var(--muted-foreground)]" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">{svc.name}</p>
              <p className="text-xs text-[var(--muted-foreground)] capitalize">{svc.status.replace(/_/g, " ")}</p>
            </div>
            {statusIcon(svc.status)}
          </motion.div>
        ))}
      </div>

      {/* Technical Info */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <h3 className="font-semibold mb-4">System Information</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            ["Version", health?.version || "1.0.0"],
            ["Uptime", `${Math.floor((health?.uptime_seconds || 0) / 60)} min`],
            ["Cameras Online", `${health?.cameras_online || 0}`],
            ["Total Cameras", `${health?.cameras_total || 0}`],
          ].map(([label, value]) => (
            <div key={label as string} className="rounded-lg bg-[var(--secondary)] p-3">
              <p className="text-xs text-[var(--muted-foreground)]">{label}</p>
              <p className="text-sm font-medium mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

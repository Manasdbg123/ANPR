"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Car, CreditCard, Camera, Activity, TrendingUp,
  ArrowUp, ArrowDown, Clock, Eye
} from "lucide-react";
import { api } from "@/lib/api";
import { formatNumber, timeAgo } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, CartesianGrid
} from "recharts";

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.4 }
  }),
};

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [hourly, setHourly] = useState<any[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  const [cameraStats, setCameraStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [ov, hr, rc, cs] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getHourlyTraffic(),
        api.getRecentDetections(8),
        api.getCameraStats(),
      ]);
      setOverview(ov.data);
      setHourly(hr.data || []);
      setRecent(rc.data || []);
      setCameraStats(cs.data || []);
    } catch (err) {
      console.error("Dashboard load error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
          ))}
        </div>
        <div className="h-72 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="h-64 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
          <div className="h-64 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: "Vehicles Today",
      value: formatNumber(overview?.vehicles_today || 0),
      icon: Car,
      color: "var(--primary)",
      sub: `${formatNumber(overview?.vehicles_this_hour || 0)} this hour`,
    },
    {
      label: "Unique Plates",
      value: formatNumber(overview?.unique_plates || 0),
      icon: CreditCard,
      color: "var(--success)",
      sub: `${formatNumber(overview?.plates_recognized || 0)} recognized`,
    },
    {
      label: "Active Cameras",
      value: String(overview?.active_cameras || 0),
      icon: Camera,
      color: "var(--info)",
      sub: "Online now",
    },
    {
      label: "Avg Confidence",
      value: `${((overview?.avg_confidence || 0) * 100).toFixed(1)}%`,
      icon: Activity,
      color: "var(--warning)",
      sub: "OCR accuracy",
    },
  ];

  return (
    <motion.div initial="hidden" animate="visible" className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            variants={fadeUp}
            custom={i}
            className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 hover:border-[var(--muted-foreground)]/20 transition"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-[var(--muted-foreground)] mb-1">{stat.label}</p>
                <p className="text-2xl font-bold tracking-tight">{stat.value}</p>
                <p className="text-xs text-[var(--muted-foreground)] mt-1">{stat.sub}</p>
              </div>
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: `color-mix(in srgb, ${stat.color} 15%, transparent)` }}
              >
                <stat.icon className="w-5 h-5" style={{ color: stat.color }} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Traffic Chart */}
      <motion.div variants={fadeUp} custom={4} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Vehicle Traffic</h3>
            <p className="text-sm text-[var(--muted-foreground)]">Hourly distribution today</p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)]">
            <Clock className="w-3.5 h-3.5" />
            Last 24 hours
          </div>
        </div>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={hourly}>
              <defs>
                <linearGradient id="colorVehicles" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="hour" stroke="#71717a" tick={{ fontSize: 11 }} tickFormatter={(h) => `${h}:00`} />
              <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#0a0a0f", border: "1px solid #27272a", borderRadius: "8px", fontSize: "12px" }}
                labelFormatter={(h) => `${h}:00 - ${h}:59`}
              />
              <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#colorVehicles)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Detections */}
        <motion.div variants={fadeUp} custom={5} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Recent Detections</h3>
            <a href="/dashboard/detections" className="text-xs text-[var(--primary)] hover:underline">View all</a>
          </div>
          {recent.length === 0 ? (
            <div className="h-40 flex items-center justify-center text-sm text-[var(--muted-foreground)]">
              <div className="text-center">
                <Eye className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>No detections yet</p>
                <p className="text-xs mt-1">Detections will appear here in real time</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {recent.map((d: any) => (
                <div key={d.id} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--secondary)] transition">
                  <div className="w-8 h-8 rounded-md bg-[var(--primary)]/10 flex items-center justify-center shrink-0">
                    <Car className="w-4 h-4 text-[var(--primary)]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium font-mono truncate">{d.plate_number || "Unknown"}</p>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {d.vehicle_color} {d.vehicle_type} • {d.camera_name || "Camera"}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs text-[var(--muted-foreground)]">{timeAgo(d.timestamp)}</p>
                    {d.plate_confidence && (
                      <p className={`text-xs ${d.plate_confidence > 0.8 ? "text-[var(--success)]" : "text-[var(--warning)]"}`}>
                        {(d.plate_confidence * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Camera Health */}
        <motion.div variants={fadeUp} custom={6} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Camera Overview</h3>
            <a href="/dashboard/cameras" className="text-xs text-[var(--primary)] hover:underline">Manage</a>
          </div>
          {cameraStats.length === 0 ? (
            <div className="h-40 flex items-center justify-center text-sm text-[var(--muted-foreground)]">
              <div className="text-center">
                <Camera className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>No cameras configured</p>
                <p className="text-xs mt-1">Add a camera to start detecting</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {cameraStats.map((cam: any) => (
                <div key={cam.camera_id} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-[var(--secondary)] transition">
                  <div className="w-2 h-2 rounded-full bg-[var(--success)]" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{cam.camera_name}</p>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {formatNumber(cam.detection_count)} detections
                    </p>
                  </div>
                  {cam.last_detection && (
                    <span className="text-xs text-[var(--muted-foreground)]">{timeAgo(cam.last_detection)}</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

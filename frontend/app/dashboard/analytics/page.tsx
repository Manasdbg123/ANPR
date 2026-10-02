"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Car, Palette } from "lucide-react";
import { api } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid
} from "recharts";

const COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6"];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [vehicleTypes, setVehicleTypes] = useState<any[]>([]);
  const [hourly, setHourly] = useState<any[]>([]);
  const [topPlates, setTopPlates] = useState<any[]>([]);
  const [cameraStats, setCameraStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [ov, vt, hr, tp, cs] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getVehicleTypes(),
        api.getHourlyTraffic(),
        api.getTopPlates(10),
        api.getCameraStats(),
      ]);
      setOverview(ov.data);
      setVehicleTypes(vt.data || []);
      setHourly(hr.data || []);
      setTopPlates(tp.data || []);
      setCameraStats(cs.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-64 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Analytics</h1>
        <p className="text-sm text-[var(--muted-foreground)]">Vehicle detection insights and trends</p>
      </div>

      {/* Hourly Traffic */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-[var(--primary)]" />
          <h3 className="font-semibold">Traffic Over Time</h3>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={hourly}>
              <defs>
                <linearGradient id="gradTraffic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="hour" stroke="#71717a" tick={{ fontSize: 11 }} tickFormatter={(h) => `${h}:00`} />
              <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#0a0a0f", border: "1px solid #27272a", borderRadius: "8px", fontSize: "12px" }}
                labelFormatter={(h) => `${h}:00`}
              />
              <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#gradTraffic)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Vehicle Type Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <Car className="w-4 h-4 text-[var(--primary)]" />
            <h3 className="font-semibold">Vehicle Types</h3>
          </div>
          {vehicleTypes.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-sm text-[var(--muted-foreground)]">
              No data available
            </div>
          ) : (
            <div className="flex items-center gap-6">
              <div className="w-40 h-40">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={vehicleTypes} dataKey="count" nameKey="vehicle_type" cx="50%" cy="50%" innerRadius={35} outerRadius={65}>
                      {vehicleTypes.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#0a0a0f", border: "1px solid #27272a", borderRadius: "8px", fontSize: "12px" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 space-y-2">
                {vehicleTypes.map((vt: any, i: number) => (
                  <div key={vt.vehicle_type} className="flex items-center gap-2 text-sm">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                    <span className="flex-1 capitalize">{vt.vehicle_type}</span>
                    <span className="text-[var(--muted-foreground)]">{vt.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Camera Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-[var(--primary)]" />
            <h3 className="font-semibold">Camera Comparison</h3>
          </div>
          {cameraStats.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-sm text-[var(--muted-foreground)]">
              No camera data
            </div>
          ) : (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cameraStats} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis type="number" stroke="#71717a" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="camera_name" type="category" stroke="#71717a" tick={{ fontSize: 11 }} width={80} />
                  <Tooltip
                    contentStyle={{ background: "#0a0a0f", border: "1px solid #27272a", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="detection_count" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </motion.div>
      </div>

      {/* Top Plates */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
      >
        <h3 className="font-semibold mb-4">Most Frequently Detected Plates</h3>
        {topPlates.length === 0 ? (
          <p className="text-sm text-[var(--muted-foreground)]">No plate data available</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="text-left px-4 py-2 font-medium">#</th>
                  <th className="text-left px-4 py-2 font-medium">Plate Number</th>
                  <th className="text-left px-4 py-2 font-medium">Detections</th>
                  <th className="text-left px-4 py-2 font-medium">Avg Confidence</th>
                </tr>
              </thead>
              <tbody>
                {topPlates.map((p: any, i: number) => (
                  <tr key={p.plate_number} className="border-b border-[var(--border)]">
                    <td className="px-4 py-2 text-[var(--muted-foreground)]">{i + 1}</td>
                    <td className="px-4 py-2 font-mono font-medium">{p.plate_number}</td>
                    <td className="px-4 py-2">{formatNumber(p.count)}</td>
                    <td className="px-4 py-2 text-[var(--success)]">{(p.avg_confidence * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}

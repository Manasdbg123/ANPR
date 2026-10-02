"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Filter, Car, X, ChevronLeft, ChevronRight, Eye, Calendar, SlidersHorizontal } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/utils";

export default function DetectionsPage() {
  const [detections, setDetections] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);
  const [filters, setFilters] = useState({
    plate_number: "",
    vehicle_type: "",
    vehicle_color: "",
    camera_id: "",
    sort_by: "timestamp",
    sort_order: "desc",
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => { loadDetections(); }, [page, filters]);

  const loadDetections = async () => {
    setLoading(true);
    try {
      const res = await api.getDetections({ ...filters, page, page_size: 20 });
      setDetections(res.data || []);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, plate_number: value });
    setPage(1);
  };

  const confidenceColor = (conf: number | null) => {
    if (!conf) return "text-[var(--muted-foreground)]";
    if (conf >= 0.9) return "text-[var(--success)]";
    if (conf >= 0.7) return "text-[var(--warning)]";
    return "text-[var(--destructive)]";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Detection History</h1>
          <p className="text-sm text-[var(--muted-foreground)]">{formatNumber(total)} total detections</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
          <input
            type="text"
            value={filters.plate_number}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full h-10 pl-10 pr-4 rounded-lg border border-[var(--border)] bg-[var(--card)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition"
            placeholder="Search plate number..."
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 h-10 rounded-lg border text-sm transition ${
            showFilters ? "border-[var(--primary)] text-[var(--primary)]" : "border-[var(--border)] text-[var(--muted-foreground)] hover:text-white"
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="text-xs text-[var(--muted-foreground)] mb-1 block">Vehicle Type</label>
                <select
                  value={filters.vehicle_type}
                  onChange={(e) => { setFilters({ ...filters, vehicle_type: e.target.value }); setPage(1); }}
                  className="w-full h-9 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
                >
                  <option value="">All Types</option>
                  <option value="car">Car</option>
                  <option value="suv">SUV</option>
                  <option value="truck">Truck</option>
                  <option value="bus">Bus</option>
                  <option value="motorcycle">Motorcycle</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-[var(--muted-foreground)] mb-1 block">Color</label>
                <select
                  value={filters.vehicle_color}
                  onChange={(e) => { setFilters({ ...filters, vehicle_color: e.target.value }); setPage(1); }}
                  className="w-full h-9 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
                >
                  <option value="">All Colors</option>
                  <option value="White">White</option>
                  <option value="Black">Black</option>
                  <option value="Silver">Silver</option>
                  <option value="Red">Red</option>
                  <option value="Blue">Blue</option>
                  <option value="Grey">Grey</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-[var(--muted-foreground)] mb-1 block">Sort By</label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
                  className="w-full h-9 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
                >
                  <option value="timestamp">Time</option>
                  <option value="plate_confidence">Confidence</option>
                  <option value="plate_number">Plate</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-[var(--muted-foreground)] mb-1 block">Order</label>
                <select
                  value={filters.sort_order}
                  onChange={(e) => setFilters({ ...filters, sort_order: e.target.value })}
                  className="w-full h-9 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
                >
                  <option value="desc">Newest First</option>
                  <option value="asc">Oldest First</option>
                </select>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
        {loading ? (
          <div className="space-y-0">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-14 border-b border-[var(--border)] animate-pulse" />
            ))}
          </div>
        ) : detections.length === 0 ? (
          <div className="py-16 text-center">
            <Eye className="w-10 h-10 mx-auto mb-3 text-[var(--muted-foreground)] opacity-30" />
            <h3 className="font-medium mb-1">No detections found</h3>
            <p className="text-sm text-[var(--muted-foreground)]">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="text-left px-4 py-3 font-medium">Plate</th>
                  <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Vehicle</th>
                  <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Camera</th>
                  <th className="text-left px-4 py-3 font-medium">Confidence</th>
                  <th className="text-left px-4 py-3 font-medium hidden sm:table-cell">Time</th>
                  <th className="text-left px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {detections.map((d: any) => (
                  <tr
                    key={d.id}
                    onClick={() => setSelected(d)}
                    className="border-b border-[var(--border)] hover:bg-[var(--secondary)] cursor-pointer transition"
                  >
                    <td className="px-4 py-3">
                      <span className="font-mono font-medium">{d.plate_number || "—"}</span>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-[var(--muted-foreground)]">
                        {d.vehicle_color} {d.vehicle_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden lg:table-cell text-[var(--muted-foreground)]">
                      {d.camera_name || "—"}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`font-mono ${confidenceColor(d.plate_confidence)}`}>
                        {d.plate_confidence ? `${(d.plate_confidence * 100).toFixed(0)}%` : "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell text-[var(--muted-foreground)] text-xs">
                      {formatDate(d.timestamp)}
                    </td>
                    <td className="px-4 py-3">
                      {d.plate_valid ? (
                        <span className="px-2 py-0.5 rounded-full bg-[var(--success)]/10 text-[var(--success)] text-xs">Valid</span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-[var(--warning)]/10 text-[var(--warning)] text-xs">Unverified</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-[var(--muted-foreground)]">
            Page {page} of {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-white disabled:opacity-30 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-white disabled:opacity-30 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Detail Side Panel */}
      <AnimatePresence>
        {selected && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setSelected(null)}
            />
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              className="fixed right-0 top-0 h-full w-full max-w-md bg-[var(--card)] border-l border-[var(--border)] z-50 overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold">Detection Detail</h2>
                  <button onClick={() => setSelected(null)} className="text-[var(--muted-foreground)] hover:text-white transition">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Plate */}
                <div className="rounded-xl bg-[var(--secondary)] p-4 mb-4 text-center">
                  <p className="text-xs text-[var(--muted-foreground)] mb-2">License Plate</p>
                  <p className="text-3xl font-bold font-mono tracking-wider">
                    {selected.plate_number || "Unknown"}
                  </p>
                  <div className="flex items-center justify-center gap-3 mt-2">
                    <span className={`text-sm ${confidenceColor(selected.plate_confidence)}`}>
                      {selected.plate_confidence ? `${(selected.plate_confidence * 100).toFixed(1)}% confidence` : "—"}
                    </span>
                    {selected.plate_valid && (
                      <span className="px-2 py-0.5 rounded-full bg-[var(--success)]/10 text-[var(--success)] text-xs">Valid</span>
                    )}
                  </div>
                </div>

                {/* Vehicle Info */}
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-[var(--muted-foreground)]">Vehicle Details</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      ["Type", selected.vehicle_type],
                      ["Color", selected.vehicle_color],
                      ["Make", selected.vehicle_make],
                      ["Model", selected.vehicle_model],
                      ["Camera", selected.camera_name],
                      ["Tracking ID", selected.tracking_id],
                      ["OCR Engine", selected.ocr_engine],
                      ["Processing", selected.processing_time_ms ? `${selected.processing_time_ms}ms` : "—"],
                    ].map(([label, value]) => (
                      <div key={label as string} className="rounded-lg bg-[var(--secondary)] px-3 py-2">
                        <p className="text-xs text-[var(--muted-foreground)]">{label}</p>
                        <p className="text-sm font-medium capitalize">{value || "—"}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timeline */}
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-3">Processing Pipeline</h3>
                  <div className="space-y-2">
                    {[
                      { step: "Frame Captured", status: "complete" },
                      { step: "Vehicle Detected", status: selected.vehicle_type ? "complete" : "skipped" },
                      { step: "Plate Detected", status: selected.plate_number ? "complete" : "skipped" },
                      { step: "OCR Processed", status: selected.ocr_engine ? "complete" : "skipped" },
                      { step: "Plate Validated", status: selected.plate_valid ? "complete" : "warning" },
                    ].map((s) => (
                      <div key={s.step} className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          s.status === "complete" ? "bg-[var(--success)]" :
                          s.status === "warning" ? "bg-[var(--warning)]" :
                          "bg-[var(--muted-foreground)]"
                        }`} />
                        <span className="text-sm">{s.step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 text-xs text-[var(--muted-foreground)]">
                  <p>Detected: {formatDate(selected.timestamp)}</p>
                  {selected.first_seen && <p>First seen: {formatDate(selected.first_seen)}</p>}
                  {selected.last_seen && <p>Last seen: {formatDate(selected.last_seen)}</p>}
                  <p>Frames: {selected.frame_count}</p>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

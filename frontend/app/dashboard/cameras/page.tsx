"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Camera, Plus, MapPin, Wifi, WifiOff, Trash2, Settings, Video } from "lucide-react";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

export default function CamerasPage() {
  const [cameras, setCameras] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [newCam, setNewCam] = useState({ name: "", location: "", rtsp_url: "", stream_type: "rtsp" });

  useEffect(() => { loadCameras(); }, []);

  const loadCameras = async () => {
    try {
      const res = await api.getCameras();
      setCameras(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addCamera = async () => {
    try {
      await api.createCamera(newCam);
      setShowAdd(false);
      setNewCam({ name: "", location: "", rtsp_url: "", stream_type: "rtsp" });
      loadCameras();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const deleteCamera = async (id: string) => {
    if (!confirm("Delete this camera?")) return;
    try {
      await api.deleteCamera(id);
      loadCameras();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-52 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Cameras</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            {cameras.length} camera{cameras.length !== 1 ? "s" : ""} configured
          </p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--primary)] text-white text-sm font-medium hover:bg-[var(--primary)]/90 transition"
        >
          <Plus className="w-4 h-4" />
          Add Camera
        </button>
      </div>

      {/* Add Camera Form */}
      {showAdd && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
        >
          <h3 className="font-semibold mb-4">Add New Camera</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Name</label>
              <input
                value={newCam.name}
                onChange={(e) => setNewCam({ ...newCam, name: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                placeholder="CAM-07"
              />
            </div>
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Location</label>
              <input
                value={newCam.location}
                onChange={(e) => setNewCam({ ...newCam, location: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                placeholder="Main Gate"
              />
            </div>
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">RTSP URL</label>
              <input
                value={newCam.rtsp_url}
                onChange={(e) => setNewCam({ ...newCam, rtsp_url: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                placeholder="rtsp://192.168.1.100:554/stream"
              />
            </div>
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Type</label>
              <select
                value={newCam.stream_type}
                onChange={(e) => setNewCam({ ...newCam, stream_type: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              >
                <option value="rtsp">RTSP</option>
                <option value="webcam">Webcam</option>
                <option value="file">Video File</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={addCamera}
              className="px-4 py-2 rounded-lg bg-[var(--primary)] text-white text-sm hover:bg-[var(--primary)]/90 transition"
            >
              Add Camera
            </button>
            <button
              onClick={() => setShowAdd(false)}
              className="px-4 py-2 rounded-lg border border-[var(--border)] text-sm text-[var(--muted-foreground)] hover:text-white transition"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Camera Grid */}
      {cameras.length === 0 ? (
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-12 text-center">
          <Camera className="w-12 h-12 mx-auto mb-4 text-[var(--muted-foreground)] opacity-30" />
          <h3 className="font-semibold mb-1">No cameras configured</h3>
          <p className="text-sm text-[var(--muted-foreground)]">Add a camera to start monitoring</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cameras.map((cam, i) => (
            <motion.div
              key={cam.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-xl border border-[var(--border)] bg-[var(--card)] overflow-hidden group hover:border-[var(--muted-foreground)]/20 transition"
            >
              {/* Camera preview area */}
              <div className="h-36 bg-gradient-to-br from-[#0f0f1a] to-[#0a0a12] relative flex items-center justify-center">
                <Video className="w-10 h-10 text-[var(--muted-foreground)] opacity-20" />
                <div className="absolute top-3 left-3 flex items-center gap-1.5">
                  <div className={`w-2 h-2 rounded-full ${cam.status === "online" ? "bg-[var(--success)] animate-pulse" : "bg-[var(--destructive)]"}`} />
                  <span className={`text-xs font-medium uppercase ${cam.status === "online" ? "text-[var(--success)]" : "text-[var(--destructive)]"}`}>
                    {cam.status}
                  </span>
                </div>
                <div className="absolute top-3 right-3">
                  <button
                    onClick={() => deleteCamera(cam.id)}
                    className="p-1.5 rounded-md bg-black/40 text-[var(--muted-foreground)] opacity-0 group-hover:opacity-100 hover:text-[var(--destructive)] transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Camera info */}
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-sm">{cam.name}</h3>
                  {cam.status === "online" ? (
                    <Wifi className="w-4 h-4 text-[var(--success)]" />
                  ) : (
                    <WifiOff className="w-4 h-4 text-[var(--muted-foreground)]" />
                  )}
                </div>
                {cam.location && (
                  <div className="flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3 text-[var(--muted-foreground)]" />
                    <span className="text-xs text-[var(--muted-foreground)]">{cam.location}</span>
                  </div>
                )}
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-[var(--border)]">
                  <span className="text-xs text-[var(--muted-foreground)]">
                    {cam.resolution_width}×{cam.resolution_height} @ {cam.fps}fps
                  </span>
                  {cam.last_heartbeat && (
                    <span className="text-xs text-[var(--muted-foreground)]">{timeAgo(cam.last_heartbeat)}</span>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

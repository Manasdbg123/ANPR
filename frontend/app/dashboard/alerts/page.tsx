"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Bell, Plus, Shield, AlertTriangle, Info, Trash2, Check } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function AlertsPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [tab, setTab] = useState<"events" | "rules">("events");
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [newRule, setNewRule] = useState({
    name: "", rule_type: "plate_match", severity: "info",
    conditions: {} as Record<string, string>,
  });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [r, e] = await Promise.all([api.getAlertRules(), api.getAlertEvents()]);
      setRules(r.data || []);
      setEvents(e.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addRule = async () => {
    try {
      await api.createAlertRule(newRule);
      setShowAdd(false);
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const acknowledgeAlert = async (id: string) => {
    try {
      await api.acknowledgeAlert(id);
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const severityIcon = (s: string) => {
    switch (s) {
      case "critical": return <Shield className="w-4 h-4 text-[var(--destructive)]" />;
      case "warning": return <AlertTriangle className="w-4 h-4 text-[var(--warning)]" />;
      default: return <Info className="w-4 h-4 text-[var(--info)]" />;
    }
  };

  const severityBg = (s: string) => {
    switch (s) {
      case "critical": return "border-[var(--destructive)]/20 bg-[var(--destructive)]/5";
      case "warning": return "border-[var(--warning)]/20 bg-[var(--warning)]/5";
      default: return "border-[var(--info)]/20 bg-[var(--info)]/5";
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Alerts</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            {events.filter((e: any) => e.status === "active").length} active alerts
          </p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--primary)] text-white text-sm hover:bg-[var(--primary)]/90 transition"
        >
          <Plus className="w-4 h-4" />
          Add Rule
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-lg bg-[var(--secondary)] w-fit">
        {(["events", "rules"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm capitalize transition ${
              tab === t ? "bg-[var(--card)] text-white shadow-sm" : "text-[var(--muted-foreground)] hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Add Rule Form */}
      {showAdd && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
        >
          <h3 className="font-semibold mb-4">New Alert Rule</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Name</label>
              <input
                value={newRule.name}
                onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                placeholder="Alert name"
              />
            </div>
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Type</label>
              <select
                value={newRule.rule_type}
                onChange={(e) => setNewRule({ ...newRule, rule_type: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
              >
                <option value="plate_match">Plate Match</option>
                <option value="unknown_plate">Unknown Plate</option>
                <option value="vehicle_type">Vehicle Type</option>
                <option value="low_confidence">Low Confidence</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Severity</label>
              <select
                value={newRule.severity}
                onChange={(e) => setNewRule({ ...newRule, severity: e.target.value })}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm"
              >
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={addRule} className="px-4 py-2 rounded-lg bg-[var(--primary)] text-white text-sm">
              Create Rule
            </button>
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 rounded-lg border border-[var(--border)] text-sm text-[var(--muted-foreground)]">
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Events */}
      {tab === "events" && (
        <div className="space-y-3">
          {events.length === 0 ? (
            <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-12 text-center">
              <Bell className="w-10 h-10 mx-auto mb-3 text-[var(--muted-foreground)] opacity-30" />
              <h3 className="font-medium mb-1">No alerts</h3>
              <p className="text-sm text-[var(--muted-foreground)]">Alerts will appear here when triggered</p>
            </div>
          ) : (
            events.map((e: any) => (
              <motion.div
                key={e.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`rounded-xl border p-4 ${severityBg(e.severity)}`}
              >
                <div className="flex items-start gap-3">
                  {severityIcon(e.severity)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{e.title}</p>
                    {e.message && <p className="text-xs text-[var(--muted-foreground)] mt-0.5">{e.message}</p>}
                    <p className="text-xs text-[var(--muted-foreground)] mt-1">{formatDate(e.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs capitalize ${
                      e.status === "active" ? "bg-[var(--warning)]/20 text-[var(--warning)]" :
                      e.status === "acknowledged" ? "bg-[var(--info)]/20 text-[var(--info)]" :
                      "bg-[var(--success)]/20 text-[var(--success)]"
                    }`}>
                      {e.status}
                    </span>
                    {e.status === "active" && (
                      <button
                        onClick={() => acknowledgeAlert(e.id)}
                        className="p-1.5 rounded-md hover:bg-white/5 transition"
                        title="Acknowledge"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}

      {/* Rules */}
      {tab === "rules" && (
        <div className="space-y-3">
          {rules.length === 0 ? (
            <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-12 text-center">
              <Shield className="w-10 h-10 mx-auto mb-3 text-[var(--muted-foreground)] opacity-30" />
              <h3 className="font-medium mb-1">No alert rules</h3>
              <p className="text-sm text-[var(--muted-foreground)]">Create rules to monitor your ANPR system</p>
            </div>
          ) : (
            rules.map((r: any) => (
              <div key={r.id} className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {severityIcon(r.severity)}
                    <div>
                      <p className="text-sm font-medium">{r.name}</p>
                      <p className="text-xs text-[var(--muted-foreground)] capitalize">{r.rule_type.replace("_", " ")} • {r.severity}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${r.enabled ? "bg-[var(--success)]/10 text-[var(--success)]" : "bg-[var(--muted)]/10 text-[var(--muted-foreground)]"}`}>
                    {r.enabled ? "Active" : "Disabled"}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

"use client";

import { motion } from "framer-motion";
import {
  Camera, Shield, Brain, BarChart3, Bell, Zap,
  ChevronRight, Scan, Eye, Activity
} from "lucide-react";
import Link from "next/link";

import type { Variants } from "framer-motion";

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: "easeOut" as const },
  }),
};

const features = [
  { icon: Camera, title: "Multi-Camera", desc: "Connect unlimited RTSP, webcam, and video sources" },
  { icon: Scan, title: "Plate Recognition", desc: "Advanced OCR with Indian plate format validation" },
  { icon: Eye, title: "Vehicle Tracking", desc: "Multi-object tracking with stable ID assignment" },
  { icon: Brain, title: "AI Assistant", desc: "Natural language queries over your ANPR data" },
  { icon: BarChart3, title: "Analytics", desc: "Real-time traffic insights and trend analysis" },
  { icon: Bell, title: "Smart Alerts", desc: "Configurable rules for plate matches and anomalies" },
  { icon: Shield, title: "Enterprise Security", desc: "JWT auth, RBAC, encrypted connections" },
  { icon: Zap, title: "GPU Accelerated", desc: "CUDA support for real-time inference" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[var(--primary)] flex items-center justify-center">
              <Scan className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg tracking-tight">VisionTrack</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm text-[var(--muted-foreground)] hover:text-white transition">
              Sign In
            </Link>
            <Link
              href="/login"
              className="text-sm px-4 py-2 rounded-lg bg-[var(--primary)] text-white hover:bg-[var(--primary)]/90 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[var(--border)] bg-[var(--secondary)] text-xs text-[var(--muted-foreground)] mb-6">
              <Activity className="w-3 h-3 text-[var(--success)]" />
              AI-Powered Vehicle Intelligence
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
              Real-Time{" "}
              <span className="gradient-text">ANPR</span>
              <br />
              Intelligence Platform
            </h1>

            <p className="text-lg md:text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto mb-8 leading-relaxed">
              Detect. Recognize. Understand. Process live camera feeds with computer vision,
              OCR, and intelligent analytics — all in real time.
            </p>

            <div className="flex items-center justify-center gap-4">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--primary)] text-white font-medium hover:bg-[var(--primary)]/90 transition"
              >
                Launch Dashboard
                <ChevronRight className="w-4 h-4" />
              </Link>
              <a
                href="#features"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-white hover:border-[var(--muted-foreground)] transition"
              >
                Learn More
              </a>
            </div>
          </motion.div>

          {/* Hero visual — simulated ANPR */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
            className="mt-16 relative"
          >
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-1 shadow-2xl shadow-black/50">
              <div className="rounded-xl bg-gradient-to-br from-[#0f0f1a] to-[#0a0a12] p-8 min-h-[320px] relative overflow-hidden">
                {/* Simulated camera feed */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/20 to-transparent" />

                {/* Detection overlay */}
                <div className="relative z-10 flex items-center justify-center h-full">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl">
                    {/* Detection Card 1 */}
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.8 }}
                      className="rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/5 p-4"
                    >
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse" />
                        <span className="text-xs text-[var(--success)]">Vehicle Detected</span>
                      </div>
                      <p className="text-2xl font-bold font-mono tracking-wider">DL01AB1234</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-[var(--muted-foreground)]">White Sedan</span>
                        <span className="text-xs text-[var(--success)]">97.4%</span>
                      </div>
                    </motion.div>

                    {/* Detection Card 2 */}
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 1.1 }}
                      className="rounded-xl border border-[var(--info)]/30 bg-[var(--info)]/5 p-4"
                    >
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-2 h-2 rounded-full bg-[var(--info)] animate-pulse" />
                        <span className="text-xs text-[var(--info)]">Tracking #T1047</span>
                      </div>
                      <p className="text-2xl font-bold font-mono tracking-wider">MH04J5678</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-[var(--muted-foreground)]">Black SUV</span>
                        <span className="text-xs text-[var(--info)]">94.2%</span>
                      </div>
                    </motion.div>

                    {/* Stats Card */}
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 1.4 }}
                      className="rounded-xl border border-[var(--border)] bg-[var(--secondary)] p-4"
                    >
                      <div className="text-xs text-[var(--muted-foreground)] mb-3">Pipeline</div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Detection</span>
                          <span className="text-[var(--success)]">12ms</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span>OCR</span>
                          <span className="text-[var(--success)]">38ms</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span>Total</span>
                          <span className="text-[var(--success)]">54ms</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span>FPS</span>
                          <span className="font-medium text-white">24</span>
                        </div>
                      </div>
                    </motion.div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="text-center mb-16"
          >
            <motion.h2 variants={fadeUp} custom={0} className="text-3xl md:text-4xl font-bold mb-4">
              Enterprise-Grade Features
            </motion.h2>
            <motion.p variants={fadeUp} custom={1} className="text-[var(--muted-foreground)] max-w-xl mx-auto">
              Everything you need for production vehicle intelligence
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i}
                className="group rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 hover:border-[var(--primary)]/40 transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-lg bg-[var(--primary)]/10 flex items-center justify-center mb-4 group-hover:bg-[var(--primary)]/20 transition">
                  <f.icon className="w-5 h-5 text-[var(--primary)]" />
                </div>
                <h3 className="font-semibold mb-1.5">{f.title}</h3>
                <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-20 px-6 border-t border-[var(--border)]">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.h2 variants={fadeUp} custom={0} className="text-3xl font-bold mb-4">
              How It Works
            </motion.h2>
            <motion.p variants={fadeUp} custom={1} className="text-[var(--muted-foreground)] mb-12">
              Frame-by-frame intelligence in milliseconds
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="flex flex-wrap items-center justify-center gap-3"
          >
            {[
              "Camera Feed", "→", "Vehicle Detection", "→", "Plate Detection", "→",
              "OCR", "→", "Validation", "→", "Tracking", "→", "Dashboard"
            ].map((step, i) => (
              <motion.span
                key={i}
                variants={fadeUp}
                custom={i * 0.5}
                className={
                  step === "→"
                    ? "text-[var(--muted-foreground)]"
                    : "px-3 py-1.5 rounded-lg bg-[var(--secondary)] border border-[var(--border)] text-sm font-medium"
                }
              >
                {step}
              </motion.span>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 border-t border-[var(--border)]">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-[var(--muted-foreground)] mb-8">
            Deploy VisionTrack ANPR in minutes. Start detecting vehicles and recognizing plates instantly.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--primary)] text-white font-medium hover:bg-[var(--primary)]/90 transition"
          >
            Launch Dashboard
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scan className="w-4 h-4 text-[var(--primary)]" />
            <span className="text-sm text-[var(--muted-foreground)]">VisionTrack ANPR</span>
          </div>
          <span className="text-xs text-[var(--muted-foreground)]">
            AI-Powered Vehicle Intelligence Platform
          </span>
        </div>
      </footer>
    </div>
  );
}

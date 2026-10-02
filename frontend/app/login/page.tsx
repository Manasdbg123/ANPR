"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Scan, Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await api.register(email, username, password, fullName || undefined);
        await api.login(username, password);
      } else {
        await api.login(username, password);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-sm"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-[var(--primary)] flex items-center justify-center">
            <Scan className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-semibold tracking-tight">VisionTrack</span>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h1 className="text-xl font-semibold mb-1">
            {isRegister ? "Create Account" : "Welcome back"}
          </h1>
          <p className="text-sm text-[var(--muted-foreground)] mb-6">
            {isRegister ? "Sign up to access the ANPR dashboard" : "Sign in to your ANPR dashboard"}
          </p>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-lg bg-[var(--destructive)]/10 border border-[var(--destructive)]/20 p-3 mb-4"
            >
              <p className="text-sm text-[var(--destructive)]">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
                    placeholder="you@company.com"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
                    placeholder="John Doe"
                  />
                </div>
              </>
            )}
            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
                placeholder="admin"
                required
              />
            </div>

            <div>
              <label className="text-sm text-[var(--muted-foreground)] mb-1.5 block">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-10 px-3 pr-10 rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] hover:text-white transition"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-10 rounded-lg bg-[var(--primary)] text-white text-sm font-medium hover:bg-[var(--primary)]/90 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {isRegister ? "Creating account..." : "Signing in..."}
                </>
              ) : (
                isRegister ? "Create Account" : "Sign In"
              )}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => { setIsRegister(!isRegister); setError(""); }}
              className="text-sm text-[var(--muted-foreground)] hover:text-[var(--primary)] transition"
            >
              {isRegister ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
            </button>
          </div>

          {/* Demo credentials */}
          <div className="mt-6 pt-4 border-t border-[var(--border)]">
            <p className="text-xs text-[var(--muted-foreground)] text-center mb-2">Demo Credentials</p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => { setUsername("admin"); setPassword("admin123"); setIsRegister(false); }}
                className="flex-1 text-xs px-3 py-2 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-white hover:border-[var(--primary)]/40 transition"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => { setUsername("operator"); setPassword("operator123"); setIsRegister(false); }}
                className="flex-1 text-xs px-3 py-2 rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] hover:text-white hover:border-[var(--primary)]/40 transition"
              >
                Operator
              </button>
            </div>
          </div>
        </div>

        <p className="text-xs text-[var(--muted-foreground)] text-center mt-6">
          <Link href="/" className="hover:text-white transition">← Back to home</Link>
        </p>
      </motion.div>
    </div>
  );
}

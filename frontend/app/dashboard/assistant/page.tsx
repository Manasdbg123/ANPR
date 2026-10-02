"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Send, User, Loader2, Sparkles, Database, BarChart3 } from "lucide-react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolCalls?: any[];
  loading?: boolean;
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "👋 I'm the **Vision Assistant**. I can help you query your ANPR data.\n\nTry asking me:\n- \"How many vehicles were detected today?\"\n- \"Show me all white SUVs\"\n- \"Which camera had the most detections?\"\n- \"Show low-confidence detections\"",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMsg },
      { role: "assistant", content: "", loading: true },
    ]);
    setLoading(true);

    try {
      const res = await api.aiQuery(userMsg);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: res.data?.response || "I couldn't process that query.",
          toolCalls: res.data?.tool_calls,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "How many vehicles today?",
    "Show white SUVs",
    "Busiest camera?",
    "Low confidence detections",
  ];

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-xl font-semibold">Vision Assistant</h1>
        <p className="text-sm text-[var(--muted-foreground)]">AI-powered ANPR data analysis</p>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 space-y-4">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                msg.role === "user"
                  ? "bg-[var(--primary)]/20"
                  : "bg-gradient-to-br from-indigo-500/20 to-purple-500/20"
              }`}>
                {msg.role === "user" ? (
                  <User className="w-4 h-4 text-[var(--primary)]" />
                ) : (
                  <Bot className="w-4 h-4 text-purple-400" />
                )}
              </div>

              <div className={`flex-1 max-w-[80%] ${msg.role === "user" ? "text-right" : ""}`}>
                {msg.loading ? (
                  <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing your query...</span>
                  </div>
                ) : (
                  <>
                    {/* Tool calls indicator */}
                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <div className="mb-2 flex flex-wrap gap-2">
                        {msg.toolCalls.map((tc: any, j: number) => (
                          <span
                            key={j}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--primary)]/10 text-[var(--primary)] text-xs"
                          >
                            <Database className="w-3 h-3" />
                            {tc.tool}
                          </span>
                        ))}
                      </div>
                    )}

                    <div
                      className={`rounded-xl p-3 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "bg-[var(--primary)] text-white inline-block text-left"
                          : "bg-[var(--secondary)]"
                      }`}
                    >
                      {/* Simple markdown rendering */}
                      {msg.content.split("\n").map((line, k) => {
                        if (line.startsWith("- **")) {
                          const parts = line.substring(2).split("**");
                          return (
                            <p key={k} className="py-0.5">
                              • <strong>{parts[1]}</strong>{parts[2]}
                            </p>
                          );
                        }
                        if (line.startsWith("**") && line.endsWith("**")) {
                          return <p key={k} className="font-semibold py-0.5">{line.replace(/\*\*/g, "")}</p>;
                        }
                        if (line.includes("**")) {
                          const parts = line.split("**");
                          return (
                            <p key={k} className="py-0.5">
                              {parts.map((p, pi) => pi % 2 === 1 ? <strong key={pi}>{p}</strong> : p)}
                            </p>
                          );
                        }
                        if (line.startsWith("- ")) {
                          return <p key={k} className="py-0.5">• {line.substring(2)}</p>;
                        }
                        if (line.match(/^\d+\./)) {
                          return <p key={k} className="py-0.5">{line}</p>;
                        }
                        return line ? <p key={k} className="py-0.5">{line}</p> : <br key={k} />;
                      })}
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 2 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => { setInput(s); }}
              className="px-3 py-1.5 rounded-lg border border-[var(--border)] text-xs text-[var(--muted-foreground)] hover:text-white hover:border-[var(--primary)]/40 transition"
            >
              <Sparkles className="w-3 h-3 inline mr-1" />
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="mt-3 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about your ANPR data..."
          className="flex-1 h-11 px-4 rounded-xl border border-[var(--border)] bg-[var(--card)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)] transition"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="h-11 w-11 rounded-xl bg-[var(--primary)] text-white flex items-center justify-center hover:bg-[var(--primary)]/90 disabled:opacity-50 transition"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}

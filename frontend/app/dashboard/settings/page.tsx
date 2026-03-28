"use client";

import { useState } from "react";
import {
    Settings,
    Save,
    Database,
    Shield,
    Bell,
    Globe,
    Palette,
    Key,
    CheckCircle2,
} from "lucide-react";

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);
    const [agentModel, setAgentModel] = useState("llama3.1-8b");
    const [temperature, setTemperature] = useState("0.3");
    const [maxTokens, setMaxTokens] = useState("2048");
    const [autoEscalate, setAutoEscalate] = useState(true);
    const [sentimentThreshold, setSentimentThreshold] = useState("0.3");
    const [notifications, setNotifications] = useState(true);

    function handleSave() {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    }

    return (
        <div className="flex flex-col gap-6 max-w-3xl">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Settings size={24} style={{ color: "var(--text-secondary)" }} /> Settings
                    </h1>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                        Configure your AI Employee and platform preferences
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    className="px-5 py-2.5 rounded-xl text-sm font-bold text-white flex items-center gap-2 transition-all"
                    style={{ background: saved ? "#22c55e" : "var(--gradient-primary)" }}
                >
                    {saved ? <><CheckCircle2 size={16} /> Saved!</> : <><Save size={16} /> Save Changes</>}
                </button>
            </div>

            {/* Agent Configuration */}
            <div className="rounded-2xl glass p-6">
                <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                    <Key size={18} style={{ color: "var(--accent-blue)" }} /> Agent Configuration
                </h2>
                <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>AI Model</label>
                        <select value={agentModel} onChange={(e) => setAgentModel(e.target.value)}
                            className="w-full px-3 py-2.5 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}>
                            <option value="llama3.1-8b">Llama 3.1 8B (Fast)</option>
                            <option value="llama3.1-70b">Llama 3.1 70B (Powerful)</option>
                            <option value="llama3.3-70b">Llama 3.3 70B (Latest)</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Temperature</label>
                        <input type="number" step="0.1" min="0" max="1" value={temperature} onChange={(e) => setTemperature(e.target.value)}
                            className="w-full px-3 py-2.5 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }} />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Max Tokens</label>
                        <input type="number" value={maxTokens} onChange={(e) => setMaxTokens(e.target.value)}
                            className="w-full px-3 py-2.5 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }} />
                    </div>
                    <div>
                        <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Sentiment Threshold</label>
                        <input type="number" step="0.05" min="0" max="1" value={sentimentThreshold} onChange={(e) => setSentimentThreshold(e.target.value)}
                            className="w-full px-3 py-2.5 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }} />
                    </div>
                </div>
            </div>

            {/* Escalation */}
            <div className="rounded-2xl glass p-6">
                <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                    <Shield size={18} style={{ color: "var(--accent-pink)" }} /> Escalation Rules
                </h2>
                <div className="flex flex-col gap-3">
                    <label className="flex items-center justify-between p-3 rounded-xl" style={{ background: "rgba(99,102,241,0.04)", border: "1px solid var(--border-primary)" }}>
                        <div>
                            <p className="text-sm font-medium">Auto-Escalate on Negative Sentiment</p>
                            <p className="text-xs" style={{ color: "var(--text-muted)" }}>Automatically escalate when sentiment drops below threshold</p>
                        </div>
                        <button onClick={() => setAutoEscalate(!autoEscalate)}
                            className="w-10 h-6 rounded-full relative transition-colors"
                            style={{ background: autoEscalate ? "var(--accent-blue)" : "rgba(99,102,241,0.2)" }}>
                            <span className="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all"
                                style={{ left: autoEscalate ? "18px" : "2px" }} />
                        </button>
                    </label>
                    {["Pricing inquiries → Always escalate", "Legal mentions → Always escalate", "Refund requests → Always escalate", "Explicit human request → Always escalate"].map((rule, i) => (
                        <div key={i} className="flex items-center gap-2 px-3 py-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                            <CheckCircle2 size={14} style={{ color: "var(--accent-cyan)" }} />
                            {rule}
                        </div>
                    ))}
                </div>
            </div>

            {/* Notifications */}
            <div className="rounded-2xl glass p-6">
                <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                    <Bell size={18} style={{ color: "var(--accent-cyan)" }} /> Notifications
                </h2>
                <label className="flex items-center justify-between p-3 rounded-xl" style={{ background: "rgba(99,102,241,0.04)", border: "1px solid var(--border-primary)" }}>
                    <div>
                        <p className="text-sm font-medium">Email Notifications</p>
                        <p className="text-xs" style={{ color: "var(--text-muted)" }}>Receive alerts for escalations and daily reports</p>
                    </div>
                    <button onClick={() => setNotifications(!notifications)}
                        className="w-10 h-6 rounded-full relative transition-colors"
                        style={{ background: notifications ? "var(--accent-blue)" : "rgba(99,102,241,0.2)" }}>
                        <span className="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all"
                            style={{ left: notifications ? "18px" : "2px" }} />
                    </button>
                </label>
            </div>

            {/* Database */}
            <div className="rounded-2xl glass p-6">
                <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                    <Database size={18} style={{ color: "var(--accent-purple)" }} /> Database
                </h2>
                <div className="flex flex-col gap-2 text-sm">
                    {[
                        { label: "Provider", value: "PostgreSQL + pgvector" },
                        { label: "Tables", value: "8 (customers, tickets, messages, ...)" },
                        { label: "Status", value: "Connected" },
                        { label: "Message Broker", value: "Apache Kafka" },
                    ].map((item, i) => (
                        <div key={i} className="flex justify-between py-2" style={{ borderBottom: "1px solid rgba(99,102,241,0.06)" }}>
                            <span style={{ color: "var(--text-muted)" }}>{item.label}</span>
                            <span className="font-medium" style={{ color: item.label === "Status" ? "var(--accent-cyan)" : "var(--text-primary)" }}>{item.value}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

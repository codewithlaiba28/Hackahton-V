"use client";

import { useState, useEffect } from "react";
import {
    Mail,
    MessageSquare,
    Globe,
    CheckCircle2,
    Clock,
    TrendingUp,
    Zap,
    BarChart3,
} from "lucide-react";

const channelData = [
    {
        name: "Gmail (Email)",
        icon: Mail,
        color: "var(--accent-blue)",
        status: "active",
        stats: {
            todayTickets: 48,
            avgResponse: "2.1s",
            resolution: "87%",
            satisfaction: "4.6/5",
        },
        config: {
            integration: "Gmail API + Pub/Sub",
            responseStyle: "Formal, detailed",
            maxLength: "500 words",
            greeting: "Required",
            signature: "Required",
        },
    },
    {
        name: "WhatsApp",
        icon: MessageSquare,
        color: "var(--accent-cyan)",
        status: "active",
        stats: {
            todayTickets: 32,
            avgResponse: "1.8s",
            resolution: "82%",
            satisfaction: "4.4/5",
        },
        config: {
            integration: "Twilio WhatsApp API",
            responseStyle: "Conversational, concise",
            maxLength: "300 characters",
            greeting: "Not required",
            signature: "Not required",
        },
    },
    {
        name: "Web Form",
        icon: Globe,
        color: "var(--accent-purple)",
        status: "active",
        stats: {
            todayTickets: 19,
            avgResponse: "2.4s",
            resolution: "90%",
            satisfaction: "4.7/5",
        },
        config: {
            integration: "FastAPI Endpoint",
            responseStyle: "Semi-formal",
            maxLength: "300 words",
            greeting: "Not required",
            signature: "Not required",
        },
    },
];

export default function ChannelsPage() {
    const [stats, setStats] = useState<Record<string, any>>({});

    useEffect(() => {
        async function fetchMetrics() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${apiUrl}/metrics/channels`);
                const data = await res.json();
                if (data.metrics) {
                    const statsMap: Record<string, any> = {};
                    data.metrics.forEach((m: any) => {
                        statsMap[m.channel] = {
                            todayTickets: m.total_conversations,
                            avgResponse: (m.p95_latency / 1000).toFixed(1) + "s",
                            resolution: ((1 - (m.escalations / Math.max(1, m.total_conversations))) * 100).toFixed(0) + "%",
                            satisfaction: (m.avg_sentiment * 5).toFixed(1) + "/5"
                        };
                    });
                    setStats(statsMap);
                }
            } catch (error) {
                console.error("Failed to fetch channel metrics", error);
            }
        }
        fetchMetrics();
    }, []);

    // Merge static config with dynamic stats
    const dynamicChannelData = channelData.map(ch => {
        const key = ch.name === "Gmail (Email)" ? "email" : ch.name === "WhatsApp" ? "whatsapp" : "web_form";
        return {
            ...ch,
            stats: stats[key] || { todayTickets: 0, avgResponse: "-", resolution: "-", satisfaction: "-" }
        };
    });

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <BarChart3 size={24} style={{ color: "var(--accent-blue)" }} /> Channel Management
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Monitor and configure all three communication channels
                </p>
            </div>

            <div className="flex flex-col gap-6">
                {dynamicChannelData.map((ch, i) => (
                    <div key={i} className="rounded-2xl glass overflow-hidden">
                        {/* Channel Header */}
                        <div className="px-6 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "rgba(99,102,241,0.08)", color: ch.color }}>
                                    <ch.icon size={22} />
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold">{ch.name}</h2>
                                    <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--accent-cyan)" }}>
                                        <CheckCircle2 size={10} /> {ch.status}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="p-6 grid md:grid-cols-2 gap-6">
                            {/* Stats */}
                            <div>
                                <h3 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>Today&apos;s Performance</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    {[
                                        { label: "Tickets", value: ch.stats.todayTickets, icon: <Zap size={14} /> },
                                        { label: "Avg Response", value: ch.stats.avgResponse, icon: <Clock size={14} /> },
                                        { label: "Resolution", value: ch.stats.resolution, icon: <TrendingUp size={14} /> },
                                        { label: "Satisfaction", value: ch.stats.satisfaction, icon: <CheckCircle2 size={14} /> },
                                    ].map((s, si) => (
                                        <div key={si} className="p-3 rounded-xl" style={{ background: "rgba(99,102,241,0.04)", border: "1px solid var(--border-primary)" }}>
                                            <div className="flex items-center gap-1 mb-1" style={{ color: ch.color }}>{s.icon}</div>
                                            <p className="text-lg font-bold">{s.value}</p>
                                            <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Config */}
                            <div>
                                <h3 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>Configuration</h3>
                                <div className="flex flex-col gap-2">
                                    {Object.entries(ch.config).map(([key, val]) => (
                                        <div key={key} className="flex justify-between py-1.5 text-sm" style={{ borderBottom: "1px solid rgba(99,102,241,0.06)" }}>
                                            <span className="capitalize" style={{ color: "var(--text-muted)" }}>{key.replace(/([A-Z])/g, " $1")}</span>
                                            <span className="font-medium" style={{ color: "var(--text-primary)" }}>{val}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

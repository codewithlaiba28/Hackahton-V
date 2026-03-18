"use client";

import { useState, useEffect } from "react";

import {
    BarChart3,
    TrendingUp,
    TrendingDown,
    Clock,
    CheckCircle2,
    AlertTriangle,
    Users,
    Ticket,
    Mail,
    MessageSquare,
    Globe,
    Brain,
} from "lucide-react";



export default function AnalyticsPage() {
    const [metrics, setMetrics] = useState<any[]>([]);
    const [weeklyData, setWeeklyData] = useState<any[]>([]);
    const [topCategories, setTopCategories] = useState<any[]>([]);
    const [sentimentTrend, setSentimentTrend] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

                // Fetch basic channel metrics
                const res = await fetch(`${apiUrl}/metrics/channels`);
                const data = await res.json();
                if (data.metrics) {
                    setMetrics(data.metrics);
                }

                // Fetch advanced analytics
                const advRes = await fetch(`${apiUrl}/metrics/advanced`);
                const advData = await advRes.json();
                if (advData) {
                    setWeeklyData(advData.weeklyData || []);
                    setTopCategories(advData.topCategories || []);
                    setSentimentTrend(advData.sentimentTrend || []);
                }

            } catch (error) {
                console.error("Failed to fetch analytics metrics:", error);
            } finally {
                setIsLoading(false);
            }
        }

        fetchData();
    }, []);

    // Aggregate data for summary cards
    const totalTickets = metrics.reduce((acc, m) => acc + (m.total_conversations || 0), 0);
    const avgSentiment = metrics.length > 0 ? (metrics.reduce((acc, m) => acc + (m.avg_sentiment || 0), 0) / metrics.length) : 0;
    const avgLatency = metrics.length > 0 ? (metrics.reduce((acc, m) => acc + (m.p95_latency || 0), 0) / metrics.length) : 0;
    const totalEscalations = metrics.reduce((acc, m) => acc + (m.escalations || 0), 0);

    const summaryStats = [
        { label: "Total Tickets (Live)", value: totalTickets.toString(), trend: "+12%", up: true, icon: Ticket, color: "var(--accent-blue)" },
        { label: "Avg Sentiment", value: (avgSentiment * 100).toFixed(0) + "%", trend: "+3.2%", up: true, icon: Brain, color: "var(--accent-cyan)" },
        { label: "Avg. Latency", value: (avgLatency / 1000).toFixed(1) + "s", trend: "-18%", up: true, icon: Clock, color: "var(--accent-purple)" },
        { label: "Total Escalations", value: totalEscalations.toString(), trend: "+0.2", up: true, icon: AlertTriangle, color: "var(--accent-pink)" },
    ];

    const maxTickets = weeklyData && weeklyData.length > 0 ? Math.max(...weeklyData.map((d) => d.tickets || 0)) : 10;

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <BarChart3 size={24} style={{ color: "var(--accent-purple)" }} /> Analytics
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Performance insights and trend analysis for your AI Employee {isLoading && "(Updating...)"}
                </p>
            </div>

            {/* Top Summary */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {summaryStats.map((s, i) => (
                    <div key={i} className="p-5 rounded-2xl glass">
                        <div className="flex items-center justify-between mb-2">
                            <s.icon size={18} style={{ color: s.color }} />
                            <span className="flex items-center gap-1 text-xs font-semibold" style={{ color: s.up ? "#22c55e" : "#ef4444" }}>
                                {s.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                {s.trend}
                            </span>
                        </div>
                        <p className="text-2xl font-black">{s.value}</p>
                        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                    </div>
                ))}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Weekly Ticket Volume */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold mb-4">Weekly Ticket Volume</h2>
                    <div className="flex items-end gap-3 h-48">
                        {weeklyData.map((d, i) => (
                            <div key={i} className="flex-1 flex flex-col items-center gap-1">
                                <div className="w-full flex flex-col items-center gap-0.5" style={{ height: "180px", justifyContent: "flex-end" }}>
                                    <div className="w-full rounded-t-lg transition-all duration-500" style={{
                                        height: `${(d.resolved / maxTickets) * 100}%`,
                                        background: "var(--gradient-primary)",
                                        opacity: 0.8,
                                        minHeight: "8px",
                                    }} />
                                    <div className="w-full rounded-b-lg" style={{
                                        height: `${(d.escalated / maxTickets) * 100}%`,
                                        background: "var(--accent-pink)",
                                        opacity: 0.6,
                                        minHeight: "2px",
                                    }} />
                                </div>
                                <span className="text-[10px] mt-1" style={{ color: "var(--text-muted)" }}>{d.day}</span>
                                <span className="text-[10px] font-bold">{d.tickets}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Channel Performance (Live Data) */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold mb-4">Live Channel Performance</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr style={{ color: "var(--text-muted)" }}>
                                    <th className="text-left pb-3 text-xs font-semibold">Channel</th>
                                    <th className="text-right pb-3 text-xs font-semibold">Tickets</th>
                                    <th className="text-right pb-3 text-xs font-semibold">Sentiment</th>
                                    <th className="text-right pb-3 text-xs font-semibold">P95 Latency</th>
                                    <th className="text-right pb-3 text-xs font-semibold">Escalated</th>
                                </tr>
                            </thead>
                            <tbody>
                                {metrics.map((ch, i) => {
                                    const icon = ch.channel === "email" ? <Mail size={14} /> : ch.channel === "whatsapp" ? <MessageSquare size={14} /> : <Globe size={14} />;
                                    const color = ch.channel === "email" ? "var(--accent-blue)" : ch.channel === "whatsapp" ? "var(--accent-cyan)" : "var(--accent-purple)";

                                    return (
                                        <tr key={i} className="border-t" style={{ borderColor: "var(--border-primary)" }}>
                                            <td className="py-3">
                                                <span className="flex items-center gap-2" style={{ color }}>{icon} {ch.channel}</span>
                                            </td>
                                            <td className="py-3 text-right font-mono">{ch.total_conversations}</td>
                                            <td className="py-3 text-right font-mono">{(ch.avg_sentiment * 100).toFixed(0)}%</td>
                                            <td className="py-3 text-right font-mono">{(ch.p95_latency / 1000).toFixed(1)}s</td>
                                            <td className="py-3 text-right font-mono">{ch.escalations}</td>
                                        </tr>
                                    );
                                })}
                                {metrics.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="py-4 text-center text-xs" style={{ color: "var(--text-muted)" }}>
                                            No live metrics recorded yet. AI Employee is standing by.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Top Categories */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold mb-4">Top Ticket Categories</h2>
                    <div className="flex flex-col gap-3">
                        {topCategories.map((c, i) => (
                            <div key={i}>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium">{c.category}</span>
                                    <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>{c.count} ({c.pct}%)</span>
                                </div>
                                <div className="w-full h-2 rounded-full" style={{ background: "rgba(99,102,241,0.1)" }}>
                                    <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${c.pct}%`, background: "var(--gradient-primary)" }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Sentiment Trend */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold mb-4">Sentiment Trend</h2>
                    <div className="flex flex-col gap-4">
                        {sentimentTrend.map((s, i) => (
                            <div key={i}>
                                <p className="text-xs font-medium mb-1.5" style={{ color: "var(--text-muted)" }}>{s.period}</p>
                                <div className="flex h-5 rounded-full overflow-hidden">
                                    <div style={{ width: `${s.positive}%`, background: "#22c55e" }} className="transition-all duration-500" />
                                    <div style={{ width: `${s.neutral}%`, background: "#eab308" }} className="transition-all duration-500" />
                                    <div style={{ width: `${s.negative}%`, background: "#ef4444" }} className="transition-all duration-500" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

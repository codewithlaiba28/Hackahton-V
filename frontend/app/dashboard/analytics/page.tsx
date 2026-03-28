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
    Zap,
} from "lucide-react";


export default function AnalyticsPage() {
    const [metrics, setMetrics] = useState<any[]>([]);
    const [weeklyData, setWeeklyData] = useState<any[]>([]);
    const [topCategories, setTopCategories] = useState<any[]>([]);
    const [sentimentTrend, setSentimentTrend] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

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

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    // Aggregate data for summary cards
    const totalTickets = metrics.reduce((acc, m) => acc + (m.total_conversations || 0), 0);
    const avgSentiment = metrics.length > 0 ? (metrics.reduce((acc, m) => acc + (m.avg_sentiment || 0), 0) / metrics.length) : 0.5;
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
        <div className="flex flex-col gap-8 animate-fade-up">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight flex items-center gap-3">
                        <BarChart3 size={28} className="text-purple-500" /> Deep Analytics
                    </h1>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                        Operational intelligence and multi-channel performance insights.
                    </p>
                </div>
                {isLoading && (
                    <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
                        <Loader2 className="w-3 h-3 animate-spin" /> REFRESHING...
                    </div>
                )}
            </div>

            {/* Top Summary */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {summaryStats.map((s, i) => (
                    <div key={i} className="p-6 rounded-2xl glass transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/10 active:scale-95 duration-200">
                        <div className="flex items-center justify-between mb-4">
                            <s.icon size={20} style={{ color: s.color }} />
                            <span className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full bg-slate-400/5" style={{ color: s.up ? "#22c55e" : "#ef4444" }}>
                                {s.up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                {s.trend}
                            </span>
                        </div>
                        <p className="text-3xl font-black tracking-tighter">{s.value}</p>
                        <p className="text-xs mt-1.5 font-bold tracking-wide uppercase opacity-50" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                    </div>
                ))}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Weekly Ticket Volume */}
                <div className="rounded-2xl glass p-6 shadow-2xl flex flex-col h-[380px] bg-slate-900/10">
                    <h2 className="text-lg font-bold mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                        <TrendingUp size={18} className="text-blue-500" /> 7-Day Volume Trend
                    </h2>
                    <div className="flex-1 flex items-end gap-3 pb-2 px-2">
                        {weeklyData.length === 0 ? (
                           <div className="w-full h-full flex items-center justify-center opacity-20 text-xs font-mono">WAITING FOR DATA...</div>
                        ) : weeklyData.map((d, i) => (
                            <div key={i} className="flex-1 flex flex-col items-center gap-3 group">
                                <div className="w-full flex flex-col items-center gap-1 relative" style={{ height: "180px", justifyContent: "flex-end" }}>
                                    {/* Tooltip on hover */}
                                    <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-white px-2 py-1 rounded text-[10px] font-mono whitespace-nowrap z-20 shadow-xl border border-white/10">
                                        T:{d.tickets} | R:{d.resolved}
                                    </div>
                                    <div className="w-full rounded-t-lg transition-all duration-700 ease-out group-hover:brightness-125" style={{
                                        height: `${(d.resolved / maxTickets) * 100}%`,
                                        background: "var(--gradient-primary)",
                                        boxShadow: "0 0 15px rgba(59, 130, 246, 0.2)",
                                        minHeight: "12px",
                                    }} />
                                    <div className="w-full rounded-b-lg border-t border-white/5" style={{
                                        height: `${(d.escalated / maxTickets) * 100}%`,
                                        background: "var(--accent-pink)",
                                        opacity: 0.6,
                                        minHeight: "4px",
                                    }} />
                                </div>
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{d.day}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Channel Performance */}
                <div className="rounded-2xl glass p-6 shadow-2xl h-[380px] overflow-hidden flex flex-col bg-slate-900/10">
                    <h2 className="text-lg font-bold mb-6 flex items-center gap-2 border-b border-white/5 pb-4">
                        <Zap size={18} className="text-cyan-400" /> 24h Channel Throughput
                    </h2>
                    <div className="overflow-x-auto flex-1 custom-scrollbar">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-slate-500 font-black text-[10px] uppercase tracking-widest border-b border-white/5">
                                    <th className="text-left py-3">Channel</th>
                                    <th className="text-right py-3">Tickets</th>
                                    <th className="text-right py-3">Sentiment</th>
                                    <th className="text-right py-3">P95 Latency</th>
                                    <th className="text-right py-3">Escalated</th>
                                </tr>
                            </thead>
                            <tbody>
                                {metrics.map((ch, i) => {
                                    const icon = ch.channel === "email" ? <Mail size={14} /> : ch.channel === "whatsapp" ? <MessageSquare size={14} /> : <Globe size={14} />;
                                    const color = ch.channel === "email" ? "var(--accent-blue)" : ch.channel === "whatsapp" ? "var(--accent-cyan)" : "var(--accent-purple)";

                                    return (
                                        <tr key={i} className="border-t border-white/5 hover:bg-white/2 transition-colors">
                                            <td className="py-4">
                                                <span className="flex items-center gap-2.5 font-bold" style={{ color }}>{icon} {ch.channel}</span>
                                            </td>
                                            <td className="py-4 text-right font-mono font-bold">{ch.total_conversations}</td>
                                            <td className="py-4 text-right font-mono">
                                                <span className={`px-2 py-0.5 rounded font-black text-[10px] ${ch.avg_sentiment >= 0.6 ? "text-green-400" : ch.avg_sentiment >= 0.3 ? "text-yellow-400" : "text-red-400"}`}>
                                                    {(ch.avg_sentiment * 100).toFixed(0)}%
                                                </span>
                                            </td>
                                            <td className="py-4 text-right font-mono text-slate-400">{(ch.p95_latency / 1000).toFixed(1)}s</td>
                                            <td className="py-4 text-right font-mono font-bold" style={{ color: ch.escalations > 0 ? "var(--accent-pink)" : "inherit" }}>{ch.escalations}</td>
                                        </tr>
                                    );
                                })}
                                {metrics.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="py-20 text-center text-[10px] font-mono uppercase tracking-widest opacity-20">
                                            SYSTEM MONITORING ACTIVE - NO RECENT EVENTS
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Top Categories */}
                <div className="rounded-2xl glass p-6 shadow-2xl h-[420px] flex flex-col bg-slate-900/10">
                    <h2 className="text-lg font-bold mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                        <Brain size={18} className="text-blue-400" /> Category Breakdown
                    </h2>
                    <div className="flex flex-col gap-6 flex-1 overflow-y-auto pr-2 custom-scrollbar">
                        {topCategories.length === 0 ? (
                             <div className="flex flex-col items-center justify-center h-full opacity-20 text-xs">NO CATEGORIZED TICKETS</div>
                        ) : topCategories.map((c, i) => (
                            <div key={i} className="group">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-bold tracking-tight text-slate-200">{c.category}</span>
                                    <span className="text-[10px] font-mono font-black text-slate-500 uppercase">{c.count} TICKETS</span>
                                </div>
                                <div className="w-full h-2.5 rounded-full bg-slate-400/5 relative overflow-hidden p-[1px]">
                                    <div className="h-full rounded-full transition-all duration-1000 ease-in-out shadow-[0_0_10px_rgba(59,130,246,0.3)]" 
                                         style={{ width: `${c.pct}%`, background: "var(--gradient-primary)" }} />
                                    <div className="absolute top-0 right-3 h-full flex items-center">
                                       <span className="text-[8px] font-bold text-slate-600">{c.pct}%</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Sentiment Trend */}
                <div className="rounded-2xl glass p-6 shadow-2xl h-[420px] flex flex-col bg-slate-900/10">
                    <h2 className="text-lg font-bold mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                        <CheckCircle2 size={18} className="text-green-500" /> Sentiment Health (4-Week)
                    </h2>
                    <div className="flex flex-col gap-8 flex-1">
                        {sentimentTrend.length === 0 ? (
                            <div className="h-full flex items-center justify-center opacity-20 text-xs text-center">NOT ENOUGH SENTIMENT SAMPLES RECORDED YET</div>
                        ) : sentimentTrend.map((s, i) => (
                            <div key={i} className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <p className="text-[10px] font-black tracking-widest uppercase text-slate-500">{s.period}</p>
                                    <div className="flex gap-4 text-[9px] font-mono tracking-tighter">
                                        <span className="text-green-400">{s.positive}% POSITIVE</span>
                                        <span className="text-yellow-400">{s.neutral}% NEUTRAL</span>
                                        <span className="text-red-400">{s.negative}% NEGATIVE</span>
                                    </div>
                                </div>
                                <div className="flex h-6 rounded-2xl overflow-hidden border border-white/5 p-[2px] bg-slate-400/5">
                                    <div style={{ width: `${s.positive}%`, background: "#22c55e", boxShadow: "inset 0 0 10px rgba(0,0,0,0.5)" }} className="transition-all duration-1000 first:rounded-l-xl" />
                                    <div style={{ width: `${s.neutral}%`, background: "#eab308", boxShadow: "inset 0 0 10px rgba(0,0,0,0.5)" }} className="transition-all duration-1000" />
                                    <div style={{ width: `${s.negative}%`, background: "#ef4444", boxShadow: "inset 0 0 10px rgba(0,0,0,0.5)" }} className="transition-all duration-1000 last:rounded-r-xl" />
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-6 p-4 rounded-xl bg-green-500/5 border border-green-500/10 text-center">
                        <p className="text-[10px] font-bold text-green-400 tracking-widest uppercase mb-1">CSI - CUSTOMER SATISFACTION INDEX</p>
                        <p className="text-lg font-black tracking-tighter">{(avgSentiment * 10).toFixed(1)} / 10.0</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Loader2({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="M12 2v4" />
            <path d="m16.2 7.8 2.9-2.9" />
            <path d="M18 12h4" />
            <path d="m16.2 16.2 2.9 2.9" />
            <path d="M12 18v4" />
            <path d="m4.9 19.1 2.9-2.9" />
            <path d="M2 12h4" />
            <path d="m4.9 4.9 2.9 2.9" />
        </svg>
    );
}

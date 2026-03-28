"use client";

import { useState, useEffect } from "react";

import {
    BarChart3,
    Ticket,
    Users,
    Clock,
    TrendingUp,
    AlertTriangle,
    CheckCircle2,
    MessageSquare,
    Mail,
    Globe,
    Zap,
    Brain,
} from "lucide-react";

const stats = [
    { label: "Total Conversations", value: "0", change: "Live", icon: Ticket, color: "var(--accent-blue)" },
    { label: "Avg Sentiment", value: "0%", change: "Overall", icon: CheckCircle2, color: "var(--accent-cyan)" },
    { label: "Avg. Latency", value: "0.0s", change: "P95", icon: Clock, color: "var(--accent-purple)" },
    { label: "Escalations", value: "0", change: "Recent", icon: AlertTriangle, color: "var(--accent-pink)" },
];


const channelBreakdown = [
    { channel: "Email", icon: Mail, count: 0, pct: 0, color: "var(--accent-blue)" },
    { channel: "WhatsApp", icon: MessageSquare, count: 0, pct: 0, color: "var(--accent-cyan)" },
    { channel: "Web Form", icon: Globe, count: 0, pct: 0, color: "var(--accent-purple)" },
];

function StatusBadge({ status }: { status: string }) {
    const colors: Record<string, { bg: string; text: string }> = {
        open: { bg: "rgba(99,102,241,0.15)", text: "var(--accent-blue)" },
        responded: { bg: "rgba(34,211,238,0.15)", text: "var(--accent-cyan)" },
        resolved: { bg: "rgba(34,197,94,0.15)", text: "#22c55e" },
        escalated: { bg: "rgba(236,72,153,0.15)", text: "var(--accent-pink)" },
    };
    const c = colors[status] || colors.open;
    return (
        <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold capitalize" style={{ background: c.bg, color: c.text }}>
            {status}
        </span>
    );
}

function PriorityDot({ priority }: { priority: string }) {
    const c: Record<string, string> = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#22c55e" };
    return <span className="w-2 h-2 rounded-full inline-block" style={{ background: c[priority] || c.medium }} />;
}

function ChannelIcon({ channel }: { channel: string }) {
    if (channel === "email") return <Mail size={14} style={{ color: "var(--accent-blue)" }} />;
    if (channel === "whatsapp") return <MessageSquare size={14} style={{ color: "var(--accent-cyan)" }} />;
    return <Globe size={14} style={{ color: "var(--accent-purple)" }} />;
}

export default function DashboardOverview() {
    const [dashboardStats, setDashboardStats] = useState(stats);
    const [breakdown, setBreakdown] = useState(channelBreakdown);
    const [recentTickets, setRecentTickets] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    async function fetchData() {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

            // Fetch Metrics
            const res = await fetch(`${apiUrl}/metrics/channels`);
            const data = await res.json();

            if (data.metrics) {
                // Update stats based on real data
                const totalConversations = data.metrics.reduce((acc: number, m: any) => acc + (m.total_conversations || 0), 0);
                const avgSentiment = data.metrics.length > 0 ? (data.metrics.reduce((acc: number, m: any) => acc + (m.avg_sentiment || 0), 0) / data.metrics.length) : 0;
                const totalEscalations = data.metrics.reduce((acc: number, m: any) => acc + (m.escalations || 0), 0);
                const avgLatency = data.metrics.length > 0 ? (data.metrics.reduce((acc: number, m: any) => acc + (m.p95_latency || 0), 0) / data.metrics.length) : 0;

                setDashboardStats([
                    { label: "Total Conversations", value: totalConversations.toString(), change: "Live", icon: Ticket, color: "var(--accent-blue)" },
                    { label: "Avg Sentiment", value: (avgSentiment * 100).toFixed(0) + "%", change: "Overall", icon: CheckCircle2, color: "var(--accent-cyan)" },
                    { label: "Avg. Response", value: (avgLatency / 1000).toFixed(1) + "s", change: "P95", icon: Clock, color: "var(--accent-purple)" },
                    { label: "Escalations", value: totalEscalations.toString(), change: "Recent", icon: AlertTriangle, color: "var(--accent-pink)" },
                ]);

                // Update breakdown
                const newBreakdown = data.metrics.length > 0 ? data.metrics.map((m: any) => {
                    const icon = m.channel === "email" ? Mail : m.channel === "whatsapp" ? MessageSquare : Globe;
                    const color = m.channel === "email" ? "var(--accent-blue)" : m.channel === "whatsapp" ? "var(--accent-cyan)" : "var(--accent-purple)";
                    const pct = totalConversations > 0 ? Math.round((m.total_conversations / totalConversations) * 100) : 0;
                    return {
                        channel: m.channel.charAt(0).toUpperCase() + m.channel.slice(1),
                        icon,
                        count: m.total_conversations,
                        pct,
                        color
                    };
                }) : channelBreakdown;
                setBreakdown(newBreakdown);
            }

            // Fetch Recent Tickets
            const ticketsRes = await fetch(`${apiUrl}/tickets?limit=5`);
            const ticketsData = await ticketsRes.json();
            if (ticketsData.tickets) {
                setRecentTickets(ticketsData.tickets.map((t: any) => ({
                    id: t.id.substring(0, 8),
                    subject: t.subject,
                    channel: t.channel,
                    status: t.status,
                    priority: t.priority,
                    time: new Date(t.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                })));
            }

        } catch (error) {
            console.error("Failed to fetch dashboard data:", error);
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        fetchData();
        // Auto-refresh every 30s
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col gap-6 animate-fade-up">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">System Overview</h1>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                        Your AI Employee is <span className="inline-flex items-center gap-1.5 font-medium" style={{ color: "var(--accent-cyan)" }}>
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" /> 
                            {isLoading ? "connecting..." : "online"}
                        </span> and processing tickets across all channels.
                    </p>
                </div>
                <div className="flex items-center gap-2 text-[10px] font-mono tracking-tighter text-slate-500 bg-slate-400/5 px-3 py-1.5 rounded-full border border-slate-400/10">
                    <Clock size={12} /> LAST SYNC: {new Date().toLocaleTimeString()}
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardStats.map((s, i) => (
                    <div key={i} className="p-5 rounded-2xl glass glass-hover transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-blue-500/10 to-transparent rounded-bl-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="flex items-center justify-between mb-3 relative z-10">
                            <s.icon size={20} style={{ color: s.color }} className="group-hover:scale-110 transition-transform" />
                            <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-slate-400/10" style={{ color: "var(--accent-cyan)" }}>
                                {s.change}
                            </span>
                        </div>
                        <p className="text-2xl font-black tracking-tight relative z-10">{s.value}</p>
                        <p className="text-xs mt-1 font-medium tracking-wide relative z-10" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Main Grid */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Recent Tickets */}
                <div className="lg:col-span-2 rounded-2xl glass p-6 shadow-xl flex flex-col min-h-[400px]">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-bold flex items-center gap-3">
                            <Ticket size={20} className="text-blue-500" /> Recent Inbound Activity
                        </h2>
                        <a href="/dashboard/tickets" className="text-xs font-bold tracking-widest uppercase hover:underline" style={{ color: "var(--accent-blue)" }}>View All Records →</a>
                    </div>
                    <div className="overflow-x-auto flex-1">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-slate-500 bg-slate-400/5">
                                    <th className="text-left px-4 py-2 font-black text-[10px] uppercase tracking-widest">ID</th>
                                    <th className="text-left px-4 py-2 font-black text-[10px] uppercase tracking-widest">Subject</th>
                                    <th className="text-left px-4 py-2 font-black text-[10px] uppercase tracking-widest">Channel</th>
                                    <th className="text-left px-4 py-2 font-black text-[10px] uppercase tracking-widest">Priority</th>
                                    <th className="text-left px-4 py-2 font-black text-[10px] uppercase tracking-widest">Status</th>
                                    <th className="text-right px-4 py-2 font-black text-[10px] uppercase tracking-widest">Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentTickets.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="py-20 text-center opacity-30 text-xs">
                                            No recent tickets detected.
                                        </td>
                                    </tr>
                                ) : recentTickets.map((t) => (
                                    <tr key={t.id} className="border-b last:border-0 hover:bg-white/5 transition-colors" style={{ borderColor: "var(--border-primary)" }}>
                                        <td className="px-4 py-4 font-mono text-xs font-bold" style={{ color: "var(--accent-blue)" }}>#{t.id}</td>
                                        <td className="px-4 py-4 font-medium max-w-[150px] truncate">{t.subject}</td>
                                        <td className="px-4 py-4"><ChannelIcon channel={t.channel} /></td>
                                        <td className="px-4 py-4"><PriorityDot priority={t.priority} /></td>
                                        <td className="px-4 py-4"><StatusBadge status={t.status} /></td>
                                        <td className="px-4 py-4 text-right text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>{t.time}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Channel Breakdown */}
                <div className="rounded-2xl glass p-6 shadow-xl flex flex-col h-full bg-slate-900/20">
                    <h2 className="text-lg font-bold flex items-center gap-3 mb-8">
                        <BarChart3 size={20} className="text-purple-500" /> Channel Distribution
                    </h2>
                    <div className="flex flex-col gap-8 flex-1">
                        {breakdown.map((ch, i) => (
                            <div key={i} className="group">
                                <div className="flex items-center justify-between mb-2.5">
                                    <span className="flex items-center gap-2.5 text-sm font-bold tracking-tight">
                                        <ch.icon size={18} style={{ color: ch.color }} /> {ch.channel}
                                    </span>
                                    <span className="text-[10px] font-mono font-black" style={{ color: "var(--text-muted)" }}>{ch.count} ({ch.pct}%)</span>
                                </div>
                                <div className="w-full h-3 rounded-full bg-slate-800/50 p-[2px] overflow-hidden">
                                    <div className="h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_8px_rgba(0,0,0,0.5)]" 
                                         style={{ width: `${ch.pct}%`, background: ch.color }} />
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Agent Status */}
                    <div className="mt-8 p-5 rounded-2xl bg-cyan-500/5 border border-cyan-500/20 shadow-inner">
                        <div className="flex items-center gap-2 mb-3">
                            <Brain size={18} className="text-cyan-400" />
                            <span className="text-sm font-black tracking-widest uppercase">Agent Core</span>
                        </div>
                        <div className="flex flex-col gap-2.5 text-[10px] font-medium" style={{ color: "var(--text-secondary)" }}>
                            <div className="flex justify-between items-center">
                                <span className="flex items-center gap-1.5"><Zap size={12} className="text-cyan-400" /> STATUS</span>
                                <span className="font-mono text-cyan-400 font-black tracking-widest">ACTIVE</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>UPTIME</span>
                                <span className="font-mono text-white">99.98%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>LATEST MODEL</span>
                                <span className="font-mono text-[9px] bg-slate-800 px-1.5 py-0.5 rounded text-white">LLAMA-3.1-70B</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

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
    { label: "Open Tickets", value: "24", change: "+3 today", icon: Ticket, color: "var(--accent-blue)" },
    { label: "Resolved Today", value: "18", change: "85% rate", icon: CheckCircle2, color: "var(--accent-cyan)" },
    { label: "Avg. Response", value: "2.4s", change: "-0.3s", icon: Clock, color: "var(--accent-purple)" },
    { label: "Escalations", value: "4", change: "16% rate", icon: AlertTriangle, color: "var(--accent-pink)" },
];


const channelBreakdown = [
    { channel: "Email", icon: Mail, count: 142, pct: 48, color: "var(--accent-blue)" },
    { channel: "WhatsApp", icon: MessageSquare, count: 98, pct: 33, color: "var(--accent-cyan)" },
    { channel: "Web Form", icon: Globe, count: 56, pct: 19, color: "var(--accent-purple)" },
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

    useEffect(() => {
        async function fetchData() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

                // Fetch Metrics
                const res = await fetch(`${apiUrl}/metrics/channels`);
                const data = await res.json();

                if (data.metrics && data.metrics.length > 0) {
                    // Update stats based on real data
                    const totalConversations = data.metrics.reduce((acc: number, m: any) => acc + (m.total_conversations || 0), 0);
                    const avgSentiment = data.metrics.reduce((acc: number, m: any) => acc + (m.avg_sentiment || 0), 0) / data.metrics.length;
                    const totalEscalations = data.metrics.reduce((acc: number, m: any) => acc + (m.escalations || 0), 0);
                    const avgLatency = data.metrics.reduce((acc: number, m: any) => acc + (m.p95_latency || 0), 0) / data.metrics.length;

                    setDashboardStats([
                        { label: "Total Conversations", value: totalConversations.toString(), change: "Live", icon: Ticket, color: "var(--accent-blue)" },
                        { label: "Avg Sentiment", value: (avgSentiment * 100).toFixed(0) + "%", change: "Overall", icon: CheckCircle2, color: "var(--accent-cyan)" },
                        { label: "Avg. Response", value: (avgLatency / 1000).toFixed(1) + "s", change: "P95", icon: Clock, color: "var(--accent-purple)" },
                        { label: "Escalations", value: totalEscalations.toString(), change: "Recent", icon: AlertTriangle, color: "var(--accent-pink)" },
                    ]);

                    // Update breakdown
                    const newBreakdown = data.metrics.map((m: any) => {
                        const icon = m.channel === "email" ? Mail : m.channel === "whatsapp" ? MessageSquare : Globe;
                        const color = m.channel === "email" ? "var(--accent-blue)" : m.channel === "whatsapp" ? "var(--accent-cyan)" : "var(--accent-purple)";
                        const pct = Math.round((m.total_conversations / totalConversations) * 100);
                        return {
                            channel: m.channel.charAt(0).toUpperCase() + m.channel.slice(1),
                            icon,
                            count: m.total_conversations,
                            pct,
                            color
                        };
                    });
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

        fetchData();
    }, []);

    return (
        <div className="flex flex-col gap-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Dashboard Overview</h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Your AI Employee is <span style={{ color: "var(--accent-cyan)" }}>● {isLoading ? "connecting..." : "online"}</span> and processing tickets across all channels.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardStats.map((s, i) => (
                    <div key={i} className="p-5 rounded-2xl glass glass-hover transition-all duration-200">
                        <div className="flex items-center justify-between mb-3">
                            <s.icon size={20} style={{ color: s.color }} />
                            <span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ background: "rgba(99,102,241,0.08)", color: "var(--accent-cyan)" }}>
                                {s.change}
                            </span>
                        </div>
                        <p className="text-2xl font-black">{s.value}</p>
                        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Main Grid */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Recent Tickets */}
                <div className="lg:col-span-2 rounded-2xl glass p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <Ticket size={18} style={{ color: "var(--accent-blue)" }} /> Recent Tickets
                        </h2>
                        <a href="/dashboard/tickets" className="text-xs font-medium" style={{ color: "var(--accent-blue)" }}>View All →</a>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr style={{ color: "var(--text-muted)" }}>
                                    <th className="text-left pb-3 font-medium text-xs">ID</th>
                                    <th className="text-left pb-3 font-medium text-xs">Subject</th>
                                    <th className="text-left pb-3 font-medium text-xs">Channel</th>
                                    <th className="text-left pb-3 font-medium text-xs">Priority</th>
                                    <th className="text-left pb-3 font-medium text-xs">Status</th>
                                    <th className="text-right pb-3 font-medium text-xs">Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentTickets.map((t) => (
                                    <tr key={t.id} className="border-t" style={{ borderColor: "var(--border-primary)" }}>
                                        <td className="py-3 font-mono text-xs" style={{ color: "var(--accent-blue)" }}>{t.id}</td>
                                        <td className="py-3">{t.subject}</td>
                                        <td className="py-3"><ChannelIcon channel={t.channel} /></td>
                                        <td className="py-3"><PriorityDot priority={t.priority} /></td>
                                        <td className="py-3"><StatusBadge status={t.status} /></td>
                                        <td className="py-3 text-right text-xs" style={{ color: "var(--text-muted)" }}>{t.time}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Channel Breakdown */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                        <BarChart3 size={18} style={{ color: "var(--accent-purple)" }} /> Channel Mix
                    </h2>
                    <div className="flex flex-col gap-5">
                        {breakdown.map((ch, i) => (
                            <div key={i}>
                                <div className="flex items-center justify-between mb-1.5">
                                    <span className="flex items-center gap-2 text-sm font-medium">
                                        <ch.icon size={16} style={{ color: ch.color }} /> {ch.channel}
                                    </span>
                                    <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>{ch.count} ({ch.pct}%)</span>
                                </div>
                                <div className="w-full h-2 rounded-full" style={{ background: "rgba(99,102,241,0.1)" }}>
                                    <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${ch.pct}%`, background: ch.color }} />
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Agent Status */}
                    <div className="mt-6 p-4 rounded-xl" style={{ background: "rgba(34,211,238,0.05)", border: "1px solid rgba(34,211,238,0.15)" }}>
                        <div className="flex items-center gap-2 mb-2">
                            <Brain size={16} style={{ color: "var(--accent-cyan)" }} />
                            <span className="text-sm font-bold">Agent Status</span>
                        </div>
                        <div className="flex items-center gap-4 text-xs" style={{ color: "var(--text-secondary)" }}>
                            <span className="flex items-center gap-1"><Zap size={12} style={{ color: "var(--accent-cyan)" }} /> Active</span>
                            <span>Uptime: 99.9%</span>
                            <span>Model: Llama 3.1 70B (Cerebras)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

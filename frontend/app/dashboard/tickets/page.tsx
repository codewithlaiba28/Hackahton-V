"use client";

import { useState, useEffect } from "react";
import {
    Ticket,
    Search,
    Filter,
    Mail,
    MessageSquare,
    Globe,
    Clock,
    ArrowUpDown,
    Loader2,
} from "lucide-react";
import { useRouter } from "next/navigation";

type TicketItem = {
    id: string;
    subject: string;
    customer: string;
    channel: "email" | "whatsapp" | "web_form";
    priority: "critical" | "high" | "medium" | "low";
    status: "open" | "responded" | "resolved" | "escalated";
    created: string;
    sentiment: number;
};



const statusColors: Record<string, { bg: string; text: string }> = {
    open: { bg: "rgba(99,102,241,0.15)", text: "var(--accent-blue)" },
    responded: { bg: "rgba(34,211,238,0.15)", text: "var(--accent-cyan)" },
    resolved: { bg: "rgba(34,197,94,0.15)", text: "#22c55e" },
    escalated: { bg: "rgba(236,72,153,0.15)", text: "var(--accent-pink)" },
};

const priorityColors: Record<string, string> = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#22c55e" };

function ChannelIcon({ channel }: { channel: string }) {
    if (channel === "email") return <Mail size={14} style={{ color: "var(--accent-blue)" }} />;
    if (channel === "whatsapp") return <MessageSquare size={14} style={{ color: "var(--accent-cyan)" }} />;
    return <Globe size={14} style={{ color: "var(--accent-purple)" }} />;
}

function SentimentBar({ score }: { score: number }) {
    const color = score >= 0.6 ? "#22c55e" : score >= 0.3 ? "#eab308" : "#ef4444";
    return (
        <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 rounded-full" style={{ background: "rgba(99,102,241,0.1)" }}>
                <div className="h-1.5 rounded-full shadow-[0_0_5px_rgba(34,197,94,0.3)] transition-all duration-500" style={{ width: `${score * 100}%`, background: color }} />
            </div>
            <span className="text-[10px] font-mono font-bold" style={{ color: "var(--text-muted)" }}>{score.toFixed(2)}</span>
        </div>
    );
}

export default function TicketsPage() {
    const router = useRouter();
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [allTickets, setAllTickets] = useState<TicketItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    async function fetchTickets() {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/tickets?limit=100`);
            const data = await res.json();
            if (data.tickets) {
                setAllTickets(data.tickets.map((t: any) => ({
                    id: t.id.substring(0, 8),
                    subject: t.subject,
                    customer: t.customer || "System User",
                    channel: t.channel,
                    priority: t.priority,
                    status: t.status,
                    created: new Date(t.time).toLocaleString([], {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    }),
                    sentiment: t.sentiment !== undefined && t.sentiment !== null ? parseFloat(t.sentiment) : 0.5
                })));
            }
        } catch (error) {
            console.error("Failed to fetch tickets:", error);
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        fetchTickets();
        const interval = setInterval(fetchTickets, 30000);
        return () => clearInterval(interval);
    }, []);

    const filtered = allTickets.filter((t) => {
        const matchSearch = (t.subject?.toLowerCase().includes(search.toLowerCase()) || "") || (t.id?.toLowerCase().includes(search.toLowerCase()) || "");
        const matchStatus = statusFilter === "all" || t.status === statusFilter;
        return matchSearch && matchStatus;
    });

    return (
        <div className="flex flex-col gap-8 animate-fade-up">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight flex items-center gap-3">
                        <Ticket size={28} className="text-blue-500" /> Ticket Management
                    </h1>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                        Comprehensive registry of all inbound support records.
                    </p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                    <div className="flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-500 uppercase bg-slate-400/5 px-3 py-1.5 rounded-full border border-slate-400/10">
                        <Clock size={12} className="animate-pulse" /> LIVE STREAM ACTIVE
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-4 bg-slate-900/40 p-2 rounded-2xl border border-white/5">
                <div className="relative flex-1 min-w-[300px]">
                    <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Filter by Subject, ID or Customer Hash..."
                        className="w-full pl-11 pr-5 py-3 rounded-xl text-sm outline-none glass focus:ring-2 focus:ring-blue-500/10 transition-all"
                        style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                    />
                </div>
                <div className="flex items-center gap-2 p-1 bg-slate-950/40 rounded-xl border border-white/5">
                    {["all", "open", "responded", "resolved", "escalated"].map((s) => (
                        <button
                            key={s}
                            onClick={() => setStatusFilter(s)}
                            className="px-4 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all"
                            style={{
                                background: statusFilter === s ? "rgba(99,102,241,0.15)" : "transparent",
                                color: statusFilter === s ? "var(--accent-blue)" : "var(--text-muted)",
                                border: `1px solid ${statusFilter === s ? "rgba(99,102,241,0.2)" : "transparent"}`,
                            }}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="rounded-3xl glass overflow-hidden shadow-2xl border-opacity-50" style={{ borderColor: "var(--border-primary)" }}>
                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="bg-slate-900/60 border-b border-white/5">
                                {["ID", "Subject", "Customer", "Channel", "Priority", "Sentiment", "Status", "Timestamp"].map((h) => (
                                    <th key={h} className="text-left px-6 py-4 font-black text-[10px] uppercase tracking-[0.2em]" style={{ color: "var(--text-muted)" }}>
                                        <div className="flex items-center gap-2 hover:text-white transition-colors cursor-pointer group">
                                            {h} <ArrowUpDown size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={8} className="py-20 text-center">
                                         <div className="flex flex-col items-center gap-3 opacity-30">
                                            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                                            <span className="text-xs font-mono uppercase tracking-widest">Accessing Datastore...</span>
                                         </div>
                                    </td>
                                </tr>
                            ) : filtered.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="py-20 text-center">
                                         <div className="flex flex-col items-center gap-3 opacity-20">
                                            <Search className="w-8 h-8" />
                                            <span className="text-xs font-mono uppercase tracking-widest">No matching records found</span>
                                         </div>
                                    </td>
                                </tr>
                            ) : filtered.map((t) => (
                                <tr key={t.id} className="transition-all hover:bg-blue-500/5 cursor-pointer group"
                                    onClick={() => router.push(`/dashboard/tickets/${t.id}`)}>
                                    <td className="px-6 py-5 font-mono text-xs font-black tracking-tighter" style={{ color: "var(--accent-blue)" }}>#{t.id}</td>
                                    <td className="px-6 py-5 font-bold text-slate-200 max-w-[200px] truncate group-hover:text-white">{t.subject}</td>
                                    <td className="px-6 py-5 text-[11px] font-medium" style={{ color: "var(--text-secondary)" }}>{t.customer}</td>
                                    <td className="px-6 py-5"><ChannelIcon channel={t.channel} /></td>
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-2 font-black text-[9px] uppercase tracking-widest px-2.5 py-1 rounded-md bg-slate-400/5 inline-flex" style={{ color: priorityColors[t.priority] }}>
                                            <div className="w-1.5 h-1.5 rounded-full" style={{ background: priorityColors[t.priority], boxShadow: `0 0 8px ${priorityColors[t.priority]}` }} />
                                            {t.priority}
                                        </div>
                                    </td>
                                    <td className="px-6 py-5"><SentimentBar score={t.sentiment} /></td>
                                    <td className="px-6 py-5">
                                        <span className="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider" style={{ background: statusColors[t.status].bg, color: statusColors[t.status].text, border: `1px solid ${statusColors[t.status].text}20` }}>
                                            {t.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-5 text-[10px] font-mono font-bold opacity-60 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-muted)" }}>{t.created}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            {/* Pagination Placeholder */}
            <div className="flex items-center justify-between px-2">
                <p className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">Showing {filtered.length} of {allTickets.length} System Records</p>
                <div className="flex gap-2">
                    <button className="px-4 py-2 rounded-lg bg-slate-400/5 border border-white/5 text-[10px] font-black uppercase tracking-widest opacity-50 cursor-not-allowed">Previous</button>
                    <button className="px-4 py-2 rounded-lg bg-slate-400/5 border border-white/5 text-[10px] font-black uppercase tracking-widest opacity-50 cursor-not-allowed">Next</button>
                </div>
            </div>
        </div>
    );
}

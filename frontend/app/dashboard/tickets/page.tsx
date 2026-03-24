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
                <div className="h-1.5 rounded-full" style={{ width: `${score * 100}%`, background: color }} />
            </div>
            <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>{score.toFixed(2)}</span>
        </div>
    );
}

export default function TicketsPage() {
    const router = useRouter();
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [allTickets, setAllTickets] = useState<TicketItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
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
        fetchTickets();
    }, []);

    const filtered = allTickets.filter((t) => {
        const matchSearch = t.subject.toLowerCase().includes(search.toLowerCase()) || t.id.toLowerCase().includes(search.toLowerCase());
        const matchStatus = statusFilter === "all" || t.status === statusFilter;
        return matchSearch && matchStatus;
    });

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Ticket size={24} style={{ color: "var(--accent-blue)" }} /> Ticket Management
                    </h1>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                        All support tickets from Email, WhatsApp, and Web channels
                    </p>
                </div>
                <div className="flex items-center gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
                    <Clock size={14} /> Updated in real-time
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3">
                <div className="relative flex-1 min-w-[200px]">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search tickets..."
                        className="w-full pl-9 pr-4 py-2.5 rounded-xl text-sm outline-none glass"
                        style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                    />
                </div>
                <div className="flex items-center gap-2">
                    <Filter size={14} style={{ color: "var(--text-muted)" }} />
                    {["all", "open", "responded", "resolved", "escalated"].map((s) => (
                        <button
                            key={s}
                            onClick={() => setStatusFilter(s)}
                            className="px-3 py-2 rounded-lg text-xs font-medium capitalize transition-colors"
                            style={{
                                background: statusFilter === s ? "rgba(99,102,241,0.15)" : "transparent",
                                color: statusFilter === s ? "var(--accent-blue)" : "var(--text-muted)",
                                border: `1px solid ${statusFilter === s ? "var(--border-hover)" : "var(--border-primary)"}`,
                            }}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="rounded-2xl glass overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr style={{ background: "rgba(99,102,241,0.04)" }}>
                                {["ID", "Subject", "Customer", "Channel", "Priority", "Sentiment", "Status", "Created"].map((h) => (
                                    <th key={h} className="text-left px-4 py-3 font-semibold text-xs" style={{ color: "var(--text-muted)" }}>
                                        <span className="flex items-center gap-1 cursor-pointer">{h} <ArrowUpDown size={10} /></span>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((t) => (
                                <tr key={t.id} className="transition-colors border-t cursor-pointer" style={{ borderColor: "var(--border-primary)" }}
                                    onClick={() => router.push(`/dashboard/tickets/${t.id}`)}
                                    onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(99,102,241,0.04)")}
                                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                                    <td className="px-4 py-3 font-mono text-xs" style={{ color: "var(--accent-blue)" }}>{t.id}</td>
                                    <td className="px-4 py-3 font-medium max-w-[250px] truncate">{t.subject}</td>
                                    <td className="px-4 py-3 text-xs" style={{ color: "var(--text-secondary)" }}>{t.customer}</td>
                                    <td className="px-4 py-3"><ChannelIcon channel={t.channel} /></td>
                                    <td className="px-4 py-3">
                                        <span className="flex items-center gap-1.5 text-xs capitalize">
                                            <span className="w-2 h-2 rounded-full" style={{ background: priorityColors[t.priority] }} />
                                            {t.priority}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3"><SentimentBar score={t.sentiment} /></td>
                                    <td className="px-4 py-3">
                                        <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold capitalize" style={{ background: statusColors[t.status].bg, color: statusColors[t.status].text }}>
                                            {t.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-xs" style={{ color: "var(--text-muted)" }}>{t.created}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

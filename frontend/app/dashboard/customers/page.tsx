"use client";

import { useState, useEffect } from "react";
import { Users, Mail, MessageSquare, Globe, Search, TrendingUp } from "lucide-react";

type Customer = {
    id: string;
    name: string;
    email: string;
    phone?: string;
    channels: string[];
    totalTickets: number;
    lastContact: string;
    sentiment: number;
    status: "active" | "idle" | "at_risk";
};



const statusStyles: Record<string, { bg: string; text: string; label: string }> = {
    active: { bg: "rgba(34,197,94,0.15)", text: "#22c55e", label: "Active" },
    idle: { bg: "rgba(234,179,8,0.15)", text: "#eab308", label: "Idle" },
    at_risk: { bg: "rgba(239,68,68,0.15)", text: "#ef4444", label: "At Risk" },
};

function ChannelBadge({ channel }: { channel: string }) {
    const icons: Record<string, React.ReactNode> = {
        email: <Mail size={12} />,
        whatsapp: <MessageSquare size={12} />,
        web_form: <Globe size={12} />,
    };
    const colors: Record<string, string> = {
        email: "var(--accent-blue)",
        whatsapp: "var(--accent-cyan)",
        web_form: "var(--accent-purple)",
    };
    return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium" style={{ background: "rgba(99,102,241,0.08)", color: colors[channel] }}>
            {icons[channel]}
        </span>
    );
}

export default function CustomersPage() {
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function fetchCustomers() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${apiUrl}/customers?limit=50`);
                const data = await res.json();
                if (data.customers) {
                    setCustomers(data.customers.map((c: any) => ({
                        id: c.id.substring(0, 8),
                        name: c.name || "Unknown User",
                        email: c.email || "-",
                        phone: c.phone || "",
                        channels: ["email"], // Simplified for real data
                        totalTickets: c.total_tickets || 0,
                        lastContact: c.last_contact ? new Date(c.last_contact).toLocaleString([], {
                            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        }) : "Never",
                        sentiment: 0.5, // Default placeholder
                        status: "active"
                    })));
                }
            } catch (error) {
                console.error("Failed to fetch customers:", error);
            } finally {
                setIsLoading(false);
            }
        }
        fetchCustomers();
    }, []);

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Users size={24} style={{ color: "var(--accent-purple)" }} /> Customer Management
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Unified customer profiles across all channels
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                {[
                    { label: "Total Customers", value: customers.length.toString(), color: "var(--accent-blue)" },
                    { label: "Active Now", value: customers.filter(c => c.status === "active").length.toString(), color: "var(--accent-cyan)" },
                    { label: "At Risk", value: customers.filter(c => c.status === "at_risk").length.toString(), color: "var(--accent-pink)" },
                ].map((s, i) => (
                    <div key={i} className="p-4 rounded-xl glass text-center">
                        <p className="text-2xl font-black" style={{ color: s.color }}>{s.value}</p>
                        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Customer Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {customers.map((c) => {
                    const ss = statusStyles[c.status];
                    return (
                        <div key={c.id} className="rounded-2xl p-5 glass glass-hover transition-all duration-200 cursor-pointer">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white" style={{ background: "var(--gradient-primary)" }}>
                                        {c.name.split(" ").map(n => n[0]).join("")}
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold">{c.name}</p>
                                        <p className="text-xs" style={{ color: "var(--text-muted)" }}>{c.email}</p>
                                    </div>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: ss.bg, color: ss.text }}>{ss.label}</span>
                            </div>

                            <div className="grid grid-cols-3 gap-2 pt-3" style={{ borderTop: "1px solid var(--border-primary)" }}>
                                <div className="text-center">
                                    <p className="text-sm font-bold">{c.totalTickets}</p>
                                    <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>Tickets</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-sm font-bold" style={{ color: c.sentiment >= 0.6 ? "#22c55e" : c.sentiment >= 0.3 ? "#eab308" : "#ef4444" }}>
                                        {(c.sentiment * 100).toFixed(0)}%
                                    </p>
                                    <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>Sentiment</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-sm font-bold">{c.lastContact}</p>
                                    <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>Last Seen</p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

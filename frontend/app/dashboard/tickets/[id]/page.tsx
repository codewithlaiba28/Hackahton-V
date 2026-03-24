"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, MessageSquare, Mail, Globe, Clock, User, CheckCircle2 } from "lucide-react";

type Message = {
    id: string;
    role: "customer" | "agent";
    content: string;
    created_at: string;
    direction: "inbound" | "outbound";
    channel: string;
    delivery_status: string;
};

type TicketDetail = {
    ticket_id: string;
    status: string;
    created_at: string;
    messages: Message[];
};

export default function TicketDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!params.id) return;

        async function fetchTicket() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${apiUrl}/support/ticket/${params.id}`);
                if (!res.ok) {
                    throw new Error("Failed to fetch ticket");
                }
                const data = await res.json();
                setTicket(data);
            } catch (err) {
                console.error(err);
                setError("Unable to load ticket details.");
            } finally {
                setIsLoading(false);
            }
        }
        fetchTicket();
    }, [params.id]);

    if (isLoading) {
        return <div className="p-8 text-center" style={{ color: "var(--text-muted)" }}>Loading ticket details...</div>;
    }

    if (error || !ticket) {
        return (
            <div className="p-8 text-center text-red-500">
                {error || "Ticket not found"}
                <button onClick={() => router.back()} className="block mt-4 text-blue-500 underline mx-auto">Go Back</button>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6 max-w-4xl mx-auto">
            <button onClick={() => router.back()} className="flex items-center gap-2 text-sm font-medium w-fit hover:opacity-80" style={{ color: "var(--text-secondary)" }}>
                <ArrowLeft size={16} /> Back to Tickets
            </button>

            <div className="glass rounded-2xl p-6">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <h1 className="text-2xl font-bold mb-2">Ticket #{ticket.ticket_id.substring(0, 8)}</h1>
                        <div className="flex items-center gap-4 text-sm" style={{ color: "var(--text-muted)" }}>
                            <span className="flex items-center gap-1"><Clock size={14} /> {new Date(ticket.created_at).toLocaleString()}</span>
                            <span className="capitalize px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: "rgba(99,102,241,0.1)", color: "var(--accent-blue)" }}>{ticket.status}</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col gap-4 mt-8">
                    <h3 className="text-lg font-semibold border-b pb-2" style={{ borderColor: "var(--border-primary)" }}>Conversation History</h3>

                    {ticket.messages && ticket.messages.length > 0 ? (
                        ticket.messages.map((msg, index) => {
                            const isCustomer = msg.role === "customer";
                            return (
                                <div key={msg.id || index} className={`flex flex-col gap-1 max-w-[80%] ${!isCustomer ? "self-end" : "self-start"}`}>
                                    <div className="flex items-center gap-2 text-xs mb-1" style={{ color: "var(--text-muted)" }}>
                                        {isCustomer ? <User size={12} /> : <MessageSquare size={12} style={{ color: "var(--accent-cyan)" }} />}
                                        <span className="uppercase font-semibold tracking-wider">{msg.role}</span>
                                        <span>•</span>
                                        <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <div className={`p-4 rounded-2xl ${isCustomer ? "rounded-tl-sm glass" : "rounded-tr-sm"}`}
                                        style={{
                                            background: !isCustomer ? "var(--gradient-primary)" : "rgba(255,255,255,0.03)",
                                            color: !isCustomer ? "#fff" : "var(--text-primary)",
                                            border: isCustomer ? "1px solid var(--border-primary)" : "none"
                                        }}>
                                        <pre className="whitespace-pre-wrap font-sans text-sm">{msg.content}</pre>
                                    </div>
                                    {/* Additional indicators showing read receipts / implementation specifics */}
                                    <div className={`flex justify-end gap-1 text-[10px] uppercase font-bold tracking-wide mt-1`} style={{ color: "var(--text-muted)", opacity: 0.7 }}>
                                        {msg.channel === 'whatsapp' && !isCustomer && (
                                            <span className="flex items-center gap-1" style={{ color: "var(--accent-blue)" }}>
                                                <CheckCircle2 size={12} /> Seen / Delivered
                                            </span>
                                        )}
                                        {msg.channel === 'email' && !isCustomer && (
                                            <span className="flex items-center gap-1 text-green-500">
                                                <Mail size={12} /> Reply-All Sent
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        <p className="text-sm italic" style={{ color: "var(--text-muted)" }}>No messages recorded for this ticket.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

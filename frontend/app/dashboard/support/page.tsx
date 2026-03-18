"use client";

import { useState } from "react";
import {
    Globe,
    Send,
    Loader2,
    CheckCircle2,
    Mail,
    User,
    FileText,
    MessageSquare,
} from "lucide-react";

export default function WebFormPage() {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [subject, setSubject] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [ticketId, setTicketId] = useState("");
    const [error, setError] = useState("");

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await fetch("/api/support", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, subject, message }),
            });

            const data = await res.json();

            if (!res.ok) {
                setError(data.error || "Submission failed");
                return;
            }

            setTicketId(data.ticket_id);
            setSubmitted(true);
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    if (submitted) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-16 h-16 rounded-full flex items-center justify-center mb-6" style={{ background: "rgba(34,197,94,0.15)" }}>
                    <CheckCircle2 size={32} style={{ color: "#22c55e" }} />
                </div>
                <h2 className="text-2xl font-bold mb-2">Ticket Submitted!</h2>
                <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
                    Your support request has been logged and our AI agent is processing it.
                </p>
                <div className="px-6 py-3 rounded-xl glass text-center">
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>Ticket ID</p>
                    <p className="text-lg font-bold font-mono" style={{ color: "var(--accent-blue)" }}>{ticketId}</p>
                </div>
                <p className="text-xs mt-4" style={{ color: "var(--text-muted)" }}>Estimated response time: Within 24 hours</p>
                <button onClick={() => { setSubmitted(false); setName(""); setEmail(""); setSubject(""); setMessage(""); }} className="mt-6 px-5 py-2 rounded-xl text-sm font-medium glass glass-hover" style={{ color: "var(--accent-blue)" }}>
                    Submit Another Ticket
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6 max-w-2xl">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Globe size={24} style={{ color: "var(--accent-purple)" }} /> Web Support Form
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Submit a support ticket that will be processed by our 24/7 AI agent
                </p>
            </div>

            {error && (
                <div className="px-4 py-3 rounded-xl text-sm" style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="rounded-2xl glass p-6 flex flex-col gap-5">
                <div className="grid sm:grid-cols-2 gap-5">
                    <div>
                        <label className="flex items-center gap-1.5 text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>
                            <User size={12} /> Full Name
                        </label>
                        <input
                            type="text"
                            required
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="John Doe"
                            className="w-full px-4 py-3 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                        />
                    </div>
                    <div>
                        <label className="flex items-center gap-1.5 text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>
                            <Mail size={12} /> Email
                        </label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@company.com"
                            className="w-full px-4 py-3 rounded-xl text-sm outline-none glass"
                            style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                        />
                    </div>
                </div>

                <div>
                    <label className="flex items-center gap-1.5 text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>
                        <FileText size={12} /> Subject
                    </label>
                    <input
                        type="text"
                        required
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        placeholder="Brief description of your issue"
                        className="w-full px-4 py-3 rounded-xl text-sm outline-none glass"
                        style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                    />
                </div>

                <div>
                    <label className="flex items-center gap-1.5 text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>
                        <MessageSquare size={12} /> Message
                    </label>
                    <textarea
                        required
                        rows={5}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Describe your issue in detail..."
                        className="w-full px-4 py-3 rounded-xl text-sm outline-none glass resize-none"
                        style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 rounded-xl font-bold text-white text-sm flex items-center justify-center gap-2 transition-all animate-gradient disabled:opacity-50"
                    style={{ background: "var(--gradient-primary)" }}
                >
                    {loading ? <><Loader2 size={16} className="animate-spin" /> Submitting...</> : <><Send size={16} /> Submit Support Ticket</>}
                </button>
            </form>

            {/* Channel info */}
            <div className="p-4 rounded-xl glass text-center">
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                    This form is one of three channels. Support is also available via{" "}
                    <span style={{ color: "var(--accent-blue)" }}>Gmail</span> and{" "}
                    <span style={{ color: "var(--accent-cyan)" }}>WhatsApp</span>.
                </p>
            </div>
        </div>
    );
}

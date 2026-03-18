"use client";

import { useState } from "react";
import {
    Brain,
    Zap,
    Clock,
    CheckCircle2,
    AlertTriangle,
    Send,
    User,
    Bot,
    Loader2,
    MessageSquare,
} from "lucide-react";

type Message = {
    role: "user" | "agent";
    content: string;
    time: string;
    channel?: string;
    tools?: string[];
};

const skillsStatus = [
    { name: "Knowledge Retrieval", status: "active", latency: "280ms", calls: 342 },
    { name: "Sentiment Analysis", status: "active", latency: "45ms", calls: 891 },
    { name: "Escalation Decision", status: "active", latency: "32ms", calls: 891 },
    { name: "Channel Adaptation", status: "active", latency: "18ms", calls: 756 },
    { name: "Customer Identification", status: "active", latency: "52ms", calls: 891 },
];

const sampleConversation: Message[] = [
    { role: "user", content: "Hi, my API key stopped working after I renewed my subscription. Can you help?", time: "10:42 AM", channel: "email" },
    { role: "agent", content: "Hello! I understand how frustrating that must be. I've found relevant documentation about API key renewals.\n\nWhen you renew your subscription, a new API key is generated automatically. You'll need to:\n\n1. Go to Settings → API Keys\n2. Copy your new key\n3. Update it in your application\n\nYour old key is deactivated for security. Would you like me to walk you through the process?", time: "10:42 AM", tools: ["create_ticket", "get_customer_history", "search_knowledge_base", "send_response"] },
    { role: "user", content: "Oh I see, thanks! Where do I find Settings?", time: "10:43 AM" },
    { role: "agent", content: "You can find Settings by clicking the gear icon (⚙️) in the top-right corner of your dashboard. Then navigate to the 'API Keys' tab in the left sidebar.\n\nLet me know if you need any further help!", time: "10:43 AM", tools: ["search_knowledge_base", "send_response"] },
];

export default function AgentPage() {
    const [messages, setMessages] = useState<Message[]>(sampleConversation);
    const [input, setInput] = useState("");
    const [processing, setProcessing] = useState(false);

    async function handleSend() {
        if (!input.trim() || processing) return;
        const userMsg: Message = { role: "user", content: input, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), channel: "web_form" };
        setMessages((prev) => [...prev, userMsg]);
        const userInput = input;
        setInput("");
        setProcessing(true);

        try {
            const res = await fetch("/api/agent/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userInput, channel: "web_form" }),
            });
            const data = await res.json();

            const agentMsg: Message = {
                role: "agent",
                content: data.response || "Sorry, I couldn't process that request.",
                time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                tools: data.tools || [],
            };
            setMessages((prev) => [...prev, agentMsg]);
        } catch {
            const errorMsg: Message = {
                role: "agent",
                content: "Sorry, there was an error processing your request. Please try again.",
                time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                tools: [],
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setProcessing(false);
        }
    }

    return (
        <div className="flex flex-col gap-6">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Brain size={24} style={{ color: "var(--accent-cyan)" }} /> AI Agent Console
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Monitor and interact with your 24/7 Customer Success FTE
                </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Chat Panel */}
                <div className="lg:col-span-2 rounded-2xl glass flex flex-col" style={{ height: "600px" }}>
                    {/* Header */}
                    <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                                <Bot size={16} className="text-white" />
                            </div>
                            <div>
                                <p className="text-sm font-bold">Customer Success FTE</p>
                                <p className="text-[10px] flex items-center gap-1" style={{ color: "var(--accent-cyan)" }}>
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" /> Online — Model: GPT-4o
                                </p>
                            </div>
                        </div>
                        <span className="text-xs px-2 py-1 rounded-full glass" style={{ color: "var(--accent-cyan)" }}>Live Demo</span>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
                        {messages.map((m, i) => (
                            <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                                <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: m.role === "agent" ? "var(--gradient-primary)" : "rgba(99,102,241,0.15)" }}>
                                    {m.role === "agent" ? <Bot size={14} className="text-white" /> : <User size={14} style={{ color: "var(--accent-blue)" }} />}
                                </div>
                                <div className={`max-w-[75%] ${m.role === "user" ? "text-right" : ""}`}>
                                    <div className="px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-line" style={{
                                        background: m.role === "agent" ? "rgba(99,102,241,0.08)" : "rgba(168,85,247,0.08)",
                                        border: `1px solid ${m.role === "agent" ? "rgba(99,102,241,0.15)" : "rgba(168,85,247,0.15)"}`,
                                    }}>
                                        {m.content}
                                    </div>
                                    <div className="flex items-center gap-2 mt-1 text-[10px]" style={{ color: "var(--text-muted)", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                                        <span>{m.time}</span>
                                        {m.tools && (
                                            <span className="flex items-center gap-1">
                                                {m.tools.map((t, ti) => (
                                                    <span key={ti} className="px-1.5 py-0.5 rounded" style={{ background: "rgba(34,211,238,0.08)", color: "var(--accent-cyan)" }}>{t}</span>
                                                ))}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {processing && (
                            <div className="flex gap-3">
                                <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                                    <Bot size={14} className="text-white" />
                                </div>
                                <div className="px-4 py-3 rounded-2xl glass text-sm flex items-center gap-2" style={{ color: "var(--text-muted)" }}>
                                    <Loader2 size={14} className="animate-spin" /> Processing...
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="px-5 py-4" style={{ borderTop: "1px solid var(--border-primary)" }}>
                        <div className="flex items-center gap-3">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                placeholder="Type a message to test the agent..."
                                className="flex-1 px-4 py-3 rounded-xl text-sm outline-none glass"
                                style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || processing}
                                className="p-3 rounded-xl text-white transition-all disabled:opacity-30"
                                style={{ background: "var(--gradient-primary)" }}
                            >
                                <Send size={16} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Skills Panel */}
                <div className="rounded-2xl glass p-5">
                    <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
                        <Zap size={18} style={{ color: "var(--accent-cyan)" }} /> Agent Skills
                    </h2>
                    <div className="flex flex-col gap-3">
                        {skillsStatus.map((s, i) => (
                            <div key={i} className="p-3 rounded-xl transition-colors" style={{ background: "rgba(99,102,241,0.04)", border: "1px solid var(--border-primary)" }}>
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium">{s.name}</span>
                                    <span className="flex items-center gap-1 text-[10px]" style={{ color: "var(--accent-cyan)" }}>
                                        <CheckCircle2 size={10} /> {s.status}
                                    </span>
                                </div>
                                <div className="flex items-center gap-4 text-[10px]" style={{ color: "var(--text-muted)" }}>
                                    <span className="flex items-center gap-1"><Clock size={10} /> {s.latency}</span>
                                    <span>{s.calls} calls today</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Agent Config */}
                    <div className="mt-6 p-4 rounded-xl" style={{ background: "rgba(99,102,241,0.04)", border: "1px solid var(--border-primary)" }}>
                        <h3 className="text-sm font-bold mb-3">Configuration</h3>
                        <div className="flex flex-col gap-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                            <div className="flex justify-between"><span>Model</span><span className="font-mono" style={{ color: "var(--text-primary)" }}>gpt-4o</span></div>
                            <div className="flex justify-between"><span>Max Tokens</span><span className="font-mono" style={{ color: "var(--text-primary)" }}>2048</span></div>
                            <div className="flex justify-between"><span>Temperature</span><span className="font-mono" style={{ color: "var(--text-primary)" }}>0.3</span></div>
                            <div className="flex justify-between"><span>Guardrails</span><span className="font-mono" style={{ color: "var(--accent-cyan)" }}>Active</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

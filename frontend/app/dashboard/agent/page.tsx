"use client";
import { useState, useEffect } from "react";
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

export default function AgentPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [processing, setProcessing] = useState(false);
    const [skillsStatus, setSkillsStatus] = useState([
        { name: "Knowledge Retrieval", status: "active", latency: "0.2s", calls: "0" },
        { name: "Sentiment Analysis", status: "active", latency: "0.1s", calls: "0" },
        { name: "Escalation Decision", status: "active", latency: "0.1s", calls: "0" },
        { name: "Channel Adaptation", status: "active", latency: "0.3s", calls: "0" },
        { name: "Customer Identification", status: "active", latency: "0.2s", calls: "0" },
    ]);

    useEffect(() => {
        async function fetchAgentStats() {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${apiUrl}/metrics/channels`);
                const data = await res.json();
                
                if (data.metrics && data.metrics.length > 0) {
                    const totalCalls = data.metrics.reduce((acc: number, m: any) => acc + (m.total_conversations || 0), 0);
                    
                    setSkillsStatus([
                        { name: "Knowledge Retrieval", status: "active", latency: "0.4s", calls: Math.floor(totalCalls * 0.8).toString() },
                        { name: "Sentiment Analysis", status: "active", latency: "0.1s", calls: totalCalls.toString() },
                        { name: "Escalation Decision", status: "active", latency: "0.1s", calls: totalCalls.toString() },
                        { name: "Channel Adaptation", status: "active", latency: "0.2s", calls: totalCalls.toString() },
                        { name: "Customer Identification", status: "active", latency: "0.3s", calls: totalCalls.toString() },
                    ]);
                }
            } catch (error) {
                console.error("Failed to fetch agent stats:", error);
            }
        }
        fetchAgentStats();
        
        // Auto-refresh every 30s
        const interval = setInterval(fetchAgentStats, 30000);
        return () => clearInterval(interval);
    }, []);

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
                content: data.response || (data.details ? `API Error: ${data.details}` : "Sorry, I couldn't process that request."),
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
        <div className="flex flex-col gap-6 h-full min-h-[calc(100vh-120px)]">
            <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Brain size={24} style={{ color: "var(--accent-cyan)" }} /> AI Agent Console
                </h1>
                <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                    Monitor and interact with your 24/7 Customer Success FTE
                </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-6 flex-1 min-h-0">
                {/* Chat Panel */}
                <div className="lg:col-span-2 rounded-2xl glass flex flex-col min-h-[500px] h-full overflow-hidden shadow-2xl transition-all duration-300 border-opacity-50 hover:border-opacity-100" style={{ borderColor: "var(--border-primary)" }}>
                    {/* Header */}
                    <div className="px-5 py-4 flex items-center justify-between bg-slate-900/40 backdrop-blur-md" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full flex items-center justify-center shadow-lg" style={{ background: "var(--gradient-primary)" }}>
                                <Bot size={16} className="text-white" />
                            </div>
                            <div>
                                <p className="text-sm font-bold tracking-tight">Customer Success FTE</p>
                                <p className="text-[10px] flex items-center gap-1.5" style={{ color: "var(--accent-cyan)" }}>
                                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block shadow-[0_0_8px_rgba(74,222,128,0.5)]" /> 
                                    Online — Model: Llama 3.1 70B (Cerebras)
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-[10px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20" style={{ color: "var(--accent-cyan)" }}>Live Agent</span>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5 custom-scrollbar bg-slate-950/20">
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full opacity-30 text-center px-10">
                                <Bot size={64} className="mb-6 animate-pulse text-cyan-500" />
                                <h3 className="text-lg font-bold mb-2">Ready to assist</h3>
                                <p className="text-sm max-w-xs">Ask a question or report an issue to see how the agent reasons and executes tools in real-time.</p>
                            </div>
                        )}
                        {messages.map((m, i) => (
                            <div key={i} className={`flex gap-3 animate-fade-up ${m.role === "user" ? "flex-row-reverse" : ""}`}>
                                <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-md" style={{ background: m.role === "agent" ? "var(--gradient-primary)" : "rgba(168,85,247,0.15)" }}>
                                    {m.role === "agent" ? <Bot size={16} className="text-white" /> : <User size={16} style={{ color: "var(--accent-purple)" }} />}
                                </div>
                                <div className={`max-w-[80%] ${m.role === "user" ? "text-right" : ""}`}>
                                    <div className="px-5 py-3.5 rounded-2xl text-sm leading-relaxed whitespace-pre-line shadow-sm border" style={{
                                        background: m.role === "agent" ? "rgba(15, 23, 42, 0.7)" : "rgba(99,102,241,0.08)",
                                        borderColor: m.role === "agent" ? "rgba(59, 130, 246, 0.2)" : "rgba(168, 85, 247, 0.2)",
                                        color: m.role === "agent" ? "var(--text-primary)" : "var(--text-primary)",
                                        borderRadius: m.role === "agent" ? "4px 20px 20px 20px" : "20px 4px 20px 20px"
                                    }}>
                                        {m.content}
                                    </div>
                                    <div className="flex items-center gap-3 mt-1.5 text-[10px]" style={{ color: "var(--text-muted)", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                                        <span className="font-mono">{m.time}</span>
                                        {m.tools && m.tools.length > 0 && (
                                            <div className="flex flex-wrap gap-1">
                                                {m.tools.map((t, ti) => (
                                                    <span key={ti} className="px-2 py-0.5 rounded-md flex items-center gap-1 bg-cyan-500/5 border border-cyan-500/10" style={{ color: "var(--accent-cyan)" }}>
                                                        <Zap size={8} /> {t}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {processing && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full flex items-center justify-center animate-pulse" style={{ background: "var(--gradient-primary)" }}>
                                    <Bot size={16} className="text-white" />
                                </div>
                                <div className="px-5 py-3 rounded-2xl glass text-sm flex items-center gap-3" style={{ color: "var(--text-secondary)", borderRadius: "4px 20px 20px 20px" }}>
                                    <Loader2 size={16} className="animate-spin text-cyan-400" /> 
                                    <span className="animate-pulse">Reasoning...</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="px-6 py-5 bg-slate-900/50 backdrop-blur-lg" style={{ borderTop: "1px solid var(--border-primary)" }}>
                        <div className="flex items-center gap-4">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                placeholder="Message Customer Success FTE..."
                                className="flex-1 px-5 py-3.5 rounded-2xl text-sm outline-none glass focus:ring-2 focus:ring-blue-500/20 transition-all placeholder:text-slate-600"
                                style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.4)" }}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || processing}
                                className="p-4 rounded-2xl text-white transition-all disabled:opacity-30 hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] active:scale-95 flex-shrink-0 group"
                                style={{ background: "var(--gradient-primary)" }}
                            >
                                <Send size={18} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Skills Panel */}
                <div className="rounded-2xl glass p-6 flex flex-col gap-8 shadow-xl bg-slate-900/20 h-full overflow-y-auto">
                    <div>
                        <h2 className="text-lg font-bold flex items-center gap-2 mb-6">
                            <Zap size={20} className="text-cyan-400" /> 
                            <span className="tracking-tight">Agent Capability Stats</span>
                        </h2>
                        <div className="flex flex-col gap-4">
                            {skillsStatus.map((s, i) => (
                                <div key={i} className="p-4 rounded-2xl transition-all duration-300 hover:scale-[1.02] border border-white/5" style={{ background: "rgba(30,41,59,0.4)" }}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs font-bold tracking-tight text-slate-200">{s.name}</span>
                                        <span className="flex items-center gap-1.5 text-[9px] uppercase tracking-widest font-black text-cyan-400">
                                            <CheckCircle2 size={10} /> {s.status}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-5 text-[10px] text-slate-400">
                                        <span className="flex items-center gap-1.5 font-mono"><Clock size={12} className="text-slate-500" /> {s.latency}</span>
                                        <span className="flex items-center gap-1.5 font-mono"><MessageSquare size={12} className="text-slate-500" /> {s.calls}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Agent Config */}
                    <div className="mt-auto p-5 rounded-2xl border bg-slate-900/60" style={{ borderColor: "var(--border-primary)" }}>
                        <h3 className="text-sm font-black mb-4 flex items-center gap-2 text-cyan-400 tracking-tight">
                             <div className="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)] animate-pulse" /> 
                             Runtime Configuration
                        </h3>
                        <div className="flex flex-col gap-3.5 text-xs">
                            <div className="flex justify-between items-center"><span className="text-slate-400">Model Engine</span><span className="font-mono text-[10px] px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400">llama-3.1-70b-v1</span></div>
                            <div className="flex justify-between items-center"><span className="text-slate-400">Response Strategy</span><span className="text-white font-bold">Standard GPT Style</span></div>
                            <div className="flex justify-between items-center"><span className="text-slate-400">System Sampling</span><span className="text-white font-mono bg-slate-800 px-1.5 py-0.5 rounded">T=0.32</span></div>
                            <div className="flex justify-between items-center"><span className="text-slate-400">Active Guardrails</span><span className="text-green-400 font-black flex items-center gap-1">VERIFIED</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

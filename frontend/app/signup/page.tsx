"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Eye, EyeOff, Loader2, Mail, Lock, User } from "lucide-react";
import { signUp } from "@/lib/auth-client";

export default function SignupPage() {
    const router = useRouter();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPw, setShowPw] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        if (password.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }
        setLoading(true);
        try {
            const { error: err } = await signUp.email({ name, email, password });
            if (err) {
                setError(err.message || "Registration failed");
            } else {
                router.push("/dashboard");
            }
        } catch {
            setError("Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "var(--gradient-hero)" }}>
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute bottom-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full" style={{ background: "radial-gradient(circle, var(--glow-purple) 0%, transparent 70%)", opacity: 0.15 }} />
            </div>

            <div className="relative z-10 w-full max-w-md">
                <Link href="/" className="flex items-center justify-center gap-2 mb-8">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                        <Bot size={22} className="text-white" />
                    </div>
                    <span className="text-2xl font-bold gradient-text">AgentForge</span>
                </Link>

                <div className="rounded-2xl p-8 glass" style={{ boxShadow: "0 0 60px rgba(168,85,247,0.08)" }}>
                    <h1 className="text-2xl font-bold text-center mb-1">Create Your Account</h1>
                    <p className="text-sm text-center mb-8" style={{ color: "var(--text-secondary)" }}>
                        Deploy your first 24/7 AI employee today
                    </p>

                    {error && (
                        <div className="mb-4 px-4 py-3 rounded-xl text-sm" style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                        <div>
                            <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Full Name</label>
                            <div className="relative">
                                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                                <input
                                    type="text"
                                    required
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="John Doe"
                                    className="w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none transition-all glass"
                                    style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Email</label>
                            <div className="relative">
                                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@company.com"
                                    className="w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none transition-all glass"
                                    style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-semibold mb-1.5" style={{ color: "var(--text-secondary)" }}>Password</label>
                            <div className="relative">
                                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                                <input
                                    type={showPw ? "text" : "password"}
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Min 8 characters"
                                    className="w-full pl-10 pr-12 py-3 rounded-xl text-sm outline-none transition-all glass"
                                    style={{ color: "var(--text-primary)", background: "rgba(5,5,16,0.5)" }}
                                />
                                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3.5 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }}>
                                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 rounded-xl font-bold text-white text-sm flex items-center justify-center gap-2 transition-all animate-gradient disabled:opacity-50"
                            style={{ background: "var(--gradient-primary)" }}
                        >
                            {loading ? <><Loader2 size={16} className="animate-spin" /> Creating Account...</> : "Create Account"}
                        </button>
                    </form>

                    <p className="text-sm text-center mt-6" style={{ color: "var(--text-secondary)" }}>
                        Already have an account?{" "}
                        <Link href="/login" className="font-semibold" style={{ color: "var(--accent-blue)" }}>
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

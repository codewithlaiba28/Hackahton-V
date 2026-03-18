"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Eye, EyeOff, Loader2, Mail, Lock } from "lucide-react";
import { signIn } from "@/lib/auth-client";

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPw, setShowPw] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const { error: err } = await signIn.email({ email, password });
            if (err) {
                setError(err.message || "Invalid credentials");
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
            {/* Background glow */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full" style={{ background: "radial-gradient(circle, var(--glow-blue) 0%, transparent 70%)", opacity: 0.15 }} />
            </div>

            <div className="relative z-10 w-full max-w-md">
                {/* Logo */}
                <Link href="/" className="flex items-center justify-center gap-2 mb-8">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
                        <Bot size={22} className="text-white" />
                    </div>
                    <span className="text-2xl font-bold gradient-text">AgentForge</span>
                </Link>

                {/* Card */}
                <div className="rounded-2xl p-8 glass" style={{ boxShadow: "0 0 60px rgba(99,102,241,0.08)" }}>
                    <h1 className="text-2xl font-bold text-center mb-1">Welcome Back</h1>
                    <p className="text-sm text-center mb-8" style={{ color: "var(--text-secondary)" }}>
                        Sign in to your AI Employee dashboard
                    </p>

                    {error && (
                        <div className="mb-4 px-4 py-3 rounded-xl text-sm" style={{ background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.2)" }}>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                        {/* Email */}
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

                        {/* Password */}
                        <div>
                            <div className="flex items-center justify-between mb-1.5">
                                <label className="text-xs font-semibold" style={{ color: "var(--text-secondary)" }}>Password</label>
                                <a href="#" className="text-xs font-medium" style={{ color: "var(--accent-blue)" }}>Forgot?</a>
                            </div>
                            <div className="relative">
                                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                                <input
                                    type={showPw ? "text" : "password"}
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
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
                            {loading ? <><Loader2 size={16} className="animate-spin" /> Signing In...</> : "Sign In"}
                        </button>
                    </form>

                    <p className="text-sm text-center mt-6" style={{ color: "var(--text-secondary)" }}>
                        Don&apos;t have an account?{" "}
                        <Link href="/signup" className="font-semibold" style={{ color: "var(--accent-blue)" }}>
                            Create one
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
    Bot,
    LayoutDashboard,
    Ticket,
    Users,
    BarChart3,
    MessageSquare,
    Brain,
    Settings,
    LogOut,
    ChevronLeft,
    ChevronRight,
    Bell,
    Search,
    Globe,
    Zap,
} from "lucide-react";
import { signOut } from "@/lib/auth-client";

const navItems = [
    { href: "/dashboard", icon: LayoutDashboard, label: "Overview" },
    { href: "/dashboard/tickets", icon: Ticket, label: "Tickets" },
    { href: "/dashboard/customers", icon: Users, label: "Customers" },
    { href: "/dashboard/agent", icon: Brain, label: "AI Agent" },
    { href: "/dashboard/channels", icon: MessageSquare, label: "Channels" },
    { href: "/dashboard/support", icon: Globe, label: "Support Form" },
    { href: "/dashboard/analytics", icon: BarChart3, label: "Analytics" },
    { href: "/dashboard/settings", icon: Settings, label: "Settings" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const router = useRouter();
    const [collapsed, setCollapsed] = useState(false);

    async function handleSignOut() {
        await signOut();
        router.push("/login");
    }

    return (
        <div className="h-screen flex overflow-hidden font-sans" style={{ background: "var(--bg-primary)" }}>
            {/* ─── LEFT SIDEBAR ─── */}
            <aside
                className="fixed left-0 top-0 bottom-0 z-40 flex flex-col transition-all duration-300 glass shadow-[10px_0_30px_rgba(0,0,0,0.5)]"
                style={{
                    width: collapsed ? "72px" : "260px",
                    borderRight: "1px solid var(--border-primary)",
                }}
            >
                {/* Logo */}
                <div className="flex items-center gap-3 px-5 py-6 bg-slate-950/20" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-[0_0_20px_rgba(59,130,246,0.3)]" style={{ background: "var(--gradient-primary)" }}>
                        <Bot size={22} className="text-white drop-shadow-md" />
                    </div>
                    {!collapsed && (
                        <div className="flex flex-col">
                            <span className="text-xl font-black gradient-text tracking-tighter leading-none">AGENTFORGE</span>
                            <span className="text-[9px] font-bold tracking-[3px] text-cyan-400 mt-1 uppercase opacity-80">Factory V2</span>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 py-6 px-3 flex flex-col gap-1.5 overflow-y-auto custom-scrollbar">
                    {navItems.map((item) => {
                        const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className="group flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all duration-300 relative overflow-hidden"
                                style={{
                                    background: active ? "rgba(59,130,246,0.12)" : "transparent",
                                    color: active ? "var(--text-primary)" : "var(--text-secondary)",
                                    boxShadow: active ? "inset 0 0 10px rgba(59,130,246,0.05)" : "none",
                                }}
                                title={collapsed ? item.label : undefined}
                            >
                                {active && <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-blue-500 rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.8)]" />}
                                <item.icon size={20} className={`flex-shrink-0 transition-all ${active ? "text-blue-400 scale-110" : "group-hover:text-white"}`} />
                                {!collapsed && <span className="tracking-tight">{item.label}</span>}
                                {active && !collapsed && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_5px_rgba(59,130,246,0.5)]" />}
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom: collapse & logout */}
                <div className="px-3 py-6 flex flex-col gap-2 bg-slate-950/20" style={{ borderTop: "1px solid var(--border-primary)" }}>
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition-all hover:bg-white/5 w-full uppercase tracking-widest text-slate-500 hover:text-white"
                    >
                        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                        {!collapsed && <span>Minimize View</span>}
                    </button>
                    <button
                        onClick={handleSignOut}
                        className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all w-full hover:bg-red-500/10 group"
                        style={{ color: "var(--accent-pink)" }}
                    >
                        <LogOut size={20} className="flex-shrink-0 transition-transform group-hover:translate-x-1" />
                        {!collapsed && <span className="tracking-tight">System Sign Out</span>}
                    </button>
                </div>
            </aside>

            {/* ─── MAIN CONTENT ─── */}
            <div className="flex-1 flex flex-col transition-all duration-300 h-full relative" style={{ marginLeft: collapsed ? "72px" : "260px" }}>
                {/* Top bar */}
                <header className="sticky top-0 z-30 flex items-center justify-between px-8 py-5 glass backdrop-blur-2xl" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                    <div className="flex items-center gap-6">
                        <div className="relative group">
                            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 transition-colors group-focus-within:text-blue-400" />
                            <input
                                type="text"
                                placeholder="Global Search (CTRL + K)"
                                className="pl-11 pr-6 py-2.5 rounded-2xl text-xs font-medium outline-none w-80 transition-all focus:w-96 focus:ring-2 focus:ring-blue-500/20 border border-transparent focus:border-blue-500/30"
                                style={{
                                    background: "rgba(5,5,16,0.6)",
                                    color: "var(--text-primary)",
                                    border: "1px solid rgba(255,255,255,0.05)"
                                }}
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 bg-slate-400/5 px-3 py-1.5 rounded-full border border-slate-400/10">
                           <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                           <span className="text-[10px] font-black tracking-widest text-slate-500 uppercase">Production Server</span>
                        </div>
                        <button className="relative p-2.5 rounded-xl transition-all hover:bg-white/5 group" style={{ color: "var(--text-secondary)" }}>
                            <Bell size={22} className="group-hover:text-white transition-colors" />
                            <span className="absolute top-2.5 right-2.5 w-2 h-2 rounded-full border-2 border-slate-900" style={{ background: "var(--accent-pink)" }} />
                        </button>
                        <div className="flex items-center gap-3 pl-2 border-l border-white/5">
                            <div className="flex flex-col items-end">
                                <span className="text-xs font-black tracking-tight">Admin Console</span>
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Master Access</span>
                            </div>
                            <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-sm font-black text-white shadow-xl hover:rotate-12 transition-transform cursor-pointer" style={{ background: "var(--gradient-primary)" }}>
                                AD
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 p-8 overflow-y-auto custom-scrollbar relative">
                    {/* Background Glow */}
                    <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[120px] -z-10 animate-pulse-slow" />
                    <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/5 rounded-full blur-[120px] -z-10 animate-pulse-slow delayed-animation" />
                    
                    <div className="relative z-10 mx-auto max-w-7xl">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}

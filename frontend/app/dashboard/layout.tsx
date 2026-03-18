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
        <div className="min-h-screen flex" style={{ background: "var(--bg-primary)" }}>
            {/* ─── LEFT SIDEBAR ─── */}
            <aside
                className="fixed left-0 top-0 bottom-0 z-40 flex flex-col transition-all duration-300 glass"
                style={{
                    width: collapsed ? "72px" : "260px",
                    borderRight: "1px solid var(--border-primary)",
                }}
            >
                {/* Logo */}
                <div className="flex items-center gap-2 px-5 py-5" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: "var(--gradient-primary)" }}>
                        <Bot size={18} className="text-white" />
                    </div>
                    {!collapsed && <span className="text-lg font-bold gradient-text whitespace-nowrap">AgentForge</span>}
                </div>

                {/* Navigation */}
                <nav className="flex-1 py-4 px-3 flex flex-col gap-1 overflow-y-auto">
                    {navItems.map((item) => {
                        const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
                                style={{
                                    background: active ? "rgba(99,102,241,0.12)" : "transparent",
                                    color: active ? "var(--accent-blue)" : "var(--text-secondary)",
                                    borderLeft: active ? "3px solid var(--accent-blue)" : "3px solid transparent",
                                }}
                                title={collapsed ? item.label : undefined}
                            >
                                <item.icon size={20} className="flex-shrink-0" />
                                {!collapsed && <span>{item.label}</span>}
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom: collapse & logout */}
                <div className="px-3 py-4 flex flex-col gap-2" style={{ borderTop: "1px solid var(--border-primary)" }}>
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors w-full"
                        style={{ color: "var(--text-muted)" }}
                    >
                        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                        {!collapsed && <span>Collapse</span>}
                    </button>
                    <button
                        onClick={handleSignOut}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors w-full"
                        style={{ color: "var(--accent-pink)" }}
                    >
                        <LogOut size={20} className="flex-shrink-0" />
                        {!collapsed && <span>Sign Out</span>}
                    </button>
                </div>
            </aside>

            {/* ─── MAIN CONTENT ─── */}
            <div className="flex-1 flex flex-col transition-all duration-300" style={{ marginLeft: collapsed ? "72px" : "260px" }}>
                {/* Top bar */}
                <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 glass" style={{ borderBottom: "1px solid var(--border-primary)" }}>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
                            <input
                                type="text"
                                placeholder="Search tickets, customers..."
                                className="pl-9 pr-4 py-2 rounded-lg text-sm outline-none w-64 transition-all"
                                style={{
                                    background: "rgba(5,5,16,0.5)",
                                    border: "1px solid var(--border-primary)",
                                    color: "var(--text-primary)",
                                }}
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button className="relative p-2 rounded-lg transition-colors" style={{ color: "var(--text-muted)" }}>
                            <Bell size={20} />
                            <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ background: "var(--accent-pink)" }} />
                        </button>
                        <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: "var(--gradient-primary)" }}>
                            U
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 p-6 overflow-y-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}

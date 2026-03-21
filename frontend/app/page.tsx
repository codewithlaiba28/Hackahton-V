"use client";

import Image from "next/image";
import Link from "next/link";
import {
  Bot,
  Mail,
  MessageSquare,
  Globe,
  Shield,
  Zap,
  BarChart3,
  Clock,
  Users,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Brain,
  Headphones,
  TrendingUp,
  GitBranch,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { useSession, signOut } from "@/lib/auth-client";

/* ─── NAV ─── */
function Navbar() {
  const [open, setOpen] = useState(false);
  const { data: session } = useSession();
  const links = [
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Channels", href: "#channels" },
    { label: "Metrics", href: "#metrics" },
    { label: "Pricing", href: "#pricing" },
  ];
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass" style={{ borderBottom: "1px solid var(--border-primary)" }}>
      <div className="mx-auto max-w-7xl flex items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
            <Bot size={20} className="text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight gradient-text">AgentForge</span>
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-8">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm font-medium transition-colors" style={{ color: "var(--text-secondary)" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}>
              {l.label}
            </a>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          {session ? (
            <>
              <Link href="/dashboard" className="px-5 py-2 rounded-lg text-sm font-medium transition-all" style={{ color: "var(--text-secondary)", border: "1px solid var(--border-primary)" }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--border-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border-primary)"; e.currentTarget.style.color = "var(--text-secondary)" }}>
                Dashboard
              </Link>
              <button onClick={() => signOut()} className="px-5 py-2 rounded-lg text-sm font-bold text-white transition-all animate-gradient" style={{ background: "var(--gradient-primary)" }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="px-5 py-2 rounded-lg text-sm font-medium transition-all" style={{ color: "var(--text-secondary)", border: "1px solid var(--border-primary)" }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--border-hover)"; e.currentTarget.style.color = "var(--text-primary)" }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border-primary)"; e.currentTarget.style.color = "var(--text-secondary)" }}>
                Sign In
              </Link>
              <Link href="/signup" className="px-5 py-2 rounded-lg text-sm font-bold text-white transition-all animate-gradient" style={{ background: "var(--gradient-primary)" }}>
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button onClick={() => setOpen(!open)} className="md:hidden" style={{ color: "var(--text-primary)" }}>
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden glass px-6 pb-6 flex flex-col gap-4" style={{ borderTop: "1px solid var(--border-primary)" }}>
          {links.map((l) => (
            <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="text-sm py-2" style={{ color: "var(--text-secondary)" }}>{l.label}</a>
          ))}
          <div className="flex gap-3 pt-2">
            {session ? (
              <button onClick={() => signOut()} className="flex-1 text-center py-2 rounded-lg text-sm font-bold text-white" style={{ background: "var(--gradient-primary)" }}>Logout</button>
            ) : (
              <>
                <Link href="/login" className="flex-1 text-center py-2 rounded-lg text-sm" style={{ border: "1px solid var(--border-primary)", color: "var(--text-secondary)" }}>Sign In</Link>
                <Link href="/signup" className="flex-1 text-center py-2 rounded-lg text-sm font-bold text-white" style={{ background: "var(--gradient-primary)" }}>Get Started</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}

/* ─── HERO ─── */
function Hero() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden" style={{ background: "var(--gradient-hero)" }}>
      {/* Particles / ambient light */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full animate-pulse-slow" style={{ background: "radial-gradient(circle, var(--glow-blue) 0%, transparent 70%)" }} />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full animate-pulse-slow" style={{ background: "radial-gradient(circle, var(--glow-purple) 0%, transparent 70%)", animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full" style={{ background: "radial-gradient(circle, var(--glow-cyan) 0%, transparent 70%)", opacity: 0.15 }} />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl w-full px-6 pt-28 pb-16 grid lg:grid-cols-2 gap-12 items-center">
        {/* Left – copy */}
        <div className="flex flex-col gap-6">
          <div className="animate-fade-up">
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide glass" style={{ color: "var(--accent-cyan)" }}>
              <Sparkles size={14} /> 24/7 AI Employee — Zero Downtime
            </span>
          </div>

          <h1 className="animate-fade-up animate-fade-up-delay-1 text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight">
            Build Your First{" "}
            <span className="gradient-text glow-text">24/7 AI&nbsp;Employee</span>
          </h1>

          <p className="animate-fade-up animate-fade-up-delay-2 text-lg leading-relaxed max-w-lg" style={{ color: "var(--text-secondary)" }}>
            A production-grade <strong style={{ color: "var(--text-primary)" }}>Customer Success FTE</strong> that handles support queries across{" "}
            <strong style={{ color: "var(--accent-blue)" }}>Email</strong>,{" "}
            <strong style={{ color: "var(--accent-cyan)" }}>WhatsApp</strong> &amp;{" "}
            <strong style={{ color: "var(--accent-purple)" }}>Web</strong> — autonomously, with empathy.
          </p>

          <div className="animate-fade-up animate-fade-up-delay-3 flex flex-wrap gap-4 pt-2">
            <Link href="/signup" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-base font-bold text-white transition-all glow-box animate-gradient" style={{ background: "var(--gradient-primary)" }}>
              Get Started Free <ArrowRight size={18} />
            </Link>
            <Link href="#how-it-works" className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-base font-medium glass glass-hover transition-all" style={{ color: "var(--text-secondary)" }}>
              See How It Works
            </Link>
          </div>

          {/* Trust bar */}
          <div className="animate-fade-up animate-fade-up-delay-4 flex items-center gap-6 pt-6">
            {[
              { icon: <Clock size={16} />, text: "< 3s Response" },
              { icon: <CheckCircle2 size={16} />, text: "85%+ Accuracy" },
              { icon: <TrendingUp size={16} />, text: "$74k/yr Saved" },
            ].map((item, i) => (
              <span key={i} className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                <span style={{ color: "var(--accent-cyan)" }}>{item.icon}</span>
                {item.text}
              </span>
            ))}
          </div>
        </div>

        {/* Right – AI head image */}
        <div className="relative flex justify-center animate-fade-up animate-fade-up-delay-3">
          <div className="relative w-[340px] h-[340px] sm:w-[440px] sm:h-[440px] animate-float">
            <div className="absolute inset-0 rounded-full" style={{ background: "radial-gradient(circle, var(--glow-blue) 0%, transparent 60%)", filter: "blur(40px)" }} />
            <Image src="/hero-ai.png" alt="AI Digital Employee" fill className="object-contain drop-shadow-2xl relative z-10" priority />
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32" style={{ background: "linear-gradient(to top, var(--bg-primary), transparent)" }} />
    </section>
  );
}

/* ─── FEATURES ─── */
const features = [
  { icon: <Brain size={28} />, title: "Intelligent Triage", desc: "Automatically classifies and routes tickets based on sentiment, urgency, and content analysis." },
  { icon: <MessageSquare size={28} />, title: "Multi-Channel Support", desc: "Seamlessly handles Email, WhatsApp, and Web form inquiries from a unified queue." },
  { icon: <Shield size={28} />, title: "Smart Escalation", desc: "Detects pricing, legal, and angry-customer patterns — escalates instantly to humans." },
  { icon: <Zap size={28} />, title: "Sub-3s Responses", desc: "Lightning-fast response generation with OpenAI Agents SDK and vector knowledge search." },
  { icon: <BarChart3 size={28} />, title: "Real-Time Analytics", desc: "Track channel metrics, sentiment trends, resolution rates, and SLA compliance." },
  { icon: <Headphones size={28} />, title: "24/7 Availability", desc: "Never sleeps, never takes vacations. Your AI employee works around the clock." },
];

function Features() {
  return (
    <section id="features" className="py-24 px-6" style={{ background: "var(--bg-primary)" }}>
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-purple)" }}>
            CAPABILITIES
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Everything Your <span className="gradient-text">AI Employee</span> Can Do
          </h2>
          <p className="mt-4 text-base max-w-2xl mx-auto" style={{ color: "var(--text-secondary)" }}>
            Purpose-built for customer success — from knowledge retrieval to ticket management, all automated.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div key={i} className="group p-6 rounded-2xl transition-all duration-300 glass glass-hover cursor-default">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-300" style={{ background: "rgba(99,102,241,0.1)", color: "var(--accent-blue)" }}>
                {f.icon}
              </div>
              <h3 className="text-lg font-bold mb-2" style={{ color: "var(--text-primary)" }}>{f.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── HOW IT WORKS ─── */
const steps = [
  { step: "01", title: "Ingest", desc: "Tickets arrive via Gmail, WhatsApp, or Web form and land in Kafka for processing.", icon: <Mail size={24} /> },
  { step: "02", title: "Analyze", desc: "The AI agent identifies the customer, analyzes sentiment, and searches the knowledge base.", icon: <Brain size={24} /> },
  { step: "03", title: "Respond", desc: "Channel-adapted responses are sent back — formal for email, concise for WhatsApp.", icon: <MessageSquare size={24} /> },
  { step: "04", title: "Learn", desc: "Every resolved ticket improves future responses through feedback loops.", icon: <GitBranch size={24} /> },
];

function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6" style={{ background: "var(--bg-secondary)" }}>
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-cyan)" }}>
            WORKFLOW
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            How <span className="gradient-text">AgentForge</span> Works
          </h2>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((s, i) => (
            <div key={i} className="relative text-center p-6 rounded-2xl glass glass-hover transition-all duration-300">
              <span className="text-5xl font-black mb-4 block" style={{ color: "rgba(99,102,241,0.15)" }}>{s.step}</span>
              <div className="w-14 h-14 rounded-full mx-auto mb-4 flex items-center justify-center" style={{ background: "rgba(99,102,241,0.1)", color: "var(--accent-blue)" }}>
                {s.icon}
              </div>
              <h3 className="text-lg font-bold mb-2">{s.title}</h3>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{s.desc}</p>
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 z-10" style={{ color: "var(--accent-blue)" }}>
                  <ArrowRight size={20} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── CHANNELS ─── */
function Channels() {
  const channels = [
    { icon: <Mail size={32} />, name: "Gmail", accent: "var(--accent-blue)", desc: "Full Gmail API integration with Pub/Sub webhooks for instant ticket ingestion.", badge: "Formal Responses" },
    { icon: <MessageSquare size={32} />, name: "WhatsApp", accent: "var(--accent-cyan)", desc: "Twilio-powered WhatsApp handler with concise, chat-style interactions.", badge: "< 300 chars" },
    { icon: <Globe size={32} />, name: "Web Form", accent: "var(--accent-purple)", desc: "Embeddable support form with real-time ticket creation and status tracking.", badge: "Semi-Formal" },
  ];

  return (
    <section id="channels" className="py-24 px-6" style={{ background: "var(--bg-primary)" }}>
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-pink)" }}>
            MULTI-CHANNEL
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            One Agent, <span className="gradient-text">Three Channels</span>
          </h2>
          <p className="mt-4 text-base max-w-2xl mx-auto" style={{ color: "var(--text-secondary)" }}>
            Your AI employee adapts its communication style to each channel automatically.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {channels.map((ch, i) => (
            <div key={i} className="p-8 rounded-2xl text-center glass glass-hover transition-all duration-300">
              <div className="w-16 h-16 rounded-2xl mx-auto mb-6 flex items-center justify-center" style={{ background: `rgba(99,102,241,0.08)`, color: ch.accent }}>
                {ch.icon}
              </div>
              <h3 className="text-xl font-bold mb-2">{ch.name}</h3>
              <span className="inline-block px-3 py-1 rounded-full text-[11px] font-semibold mb-4" style={{ background: "rgba(99,102,241,0.1)", color: ch.accent }}>{ch.badge}</span>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{ch.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── METRICS ─── */
function Metrics() {
  const metrics = [
    { value: "< $1K", label: "Annual Cost", sub: "vs $75K human FTE" },
    { value: "24/7", label: "Availability", sub: "Zero downtime" },
    { value: "<3s", label: "Response Time", sub: "Processing speed" },
    { value: "85%+", label: "Accuracy", sub: "On test queries" },
    { value: "<20%", label: "Escalation Rate", sub: "Human handoff" },
    { value: "95%+", label: "Cross-Channel ID", sub: "Customer matching" },
  ];

  return (
    <section id="metrics" className="py-24 px-6" style={{ background: "var(--bg-secondary)" }}>
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-blue)" }}>
            PERFORMANCE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Built for <span className="gradient-text">Production</span>
          </h2>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6">
          {metrics.map((m, i) => (
            <div key={i} className="p-5 rounded-2xl text-center glass glass-hover transition-all duration-300">
              <p className="text-2xl sm:text-3xl font-black gradient-text mb-1">{m.value}</p>
              <p className="text-sm font-semibold mb-1" style={{ color: "var(--text-primary)" }}>{m.label}</p>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>{m.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── TECH STACK ─── */
function TechStack() {
  const tech = [
    "OpenAI Agents SDK", "FastAPI", "PostgreSQL + pgvector",
    "Apache Kafka", "Kubernetes", "Next.js",
    "Better Auth", "Twilio", "Gmail API",
  ];
  return (
    <section className="py-24 px-6" style={{ background: "var(--bg-primary)" }}>
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-12">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-cyan)" }}>
            STACK
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Production-Grade <span className="gradient-text">Tech Stack</span>
          </h2>
        </div>
        <div className="flex flex-wrap justify-center gap-4">
          {tech.map((t, i) => (
            <span key={i} className="px-5 py-2.5 rounded-xl text-sm font-medium glass glass-hover transition-all duration-300 cursor-default" style={{ color: "var(--text-secondary)" }}>
              {t}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─── PRICING ─── */
function Pricing() {
  return (
    <section id="pricing" className="py-24 px-6" style={{ background: "var(--bg-secondary)" }}>
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 rounded-full text-xs font-semibold tracking-wide mb-4 glass" style={{ color: "var(--accent-purple)" }}>
            PRICING
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Replace a $75K FTE for <span className="gradient-text">Under $1K/yr</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {/* Human */}
          <div className="p-8 rounded-2xl glass" style={{ opacity: 0.7 }}>
            <Users size={28} style={{ color: "var(--text-muted)" }} />
            <h3 className="text-xl font-bold mt-4 mb-2" style={{ color: "var(--text-muted)" }}>Human FTE</h3>
            <p className="text-4xl font-black mb-1" style={{ color: "var(--text-muted)" }}>$75,000<span className="text-lg font-normal">/yr</span></p>
            <p className="text-sm mb-6" style={{ color: "var(--text-muted)" }}>+ benefits, training, management</p>
            <ul className="flex flex-col gap-2.5 text-sm" style={{ color: "var(--text-muted)" }}>
              {["8-hour shifts", "Sick days & vacations", "Training overhead", "Limited scalability"].map((x, i) => (
                <li key={i} className="flex items-center gap-2"><X size={14} style={{ color: "var(--accent-pink)" }} /> {x}</li>
              ))}
            </ul>
          </div>

          {/* AI */}
          <div className="p-8 rounded-2xl glass glow-box relative overflow-hidden">
            <div className="absolute top-0 right-0 px-4 py-1 text-xs font-bold text-white rounded-bl-xl" style={{ background: "var(--gradient-primary)" }}>RECOMMENDED</div>
            <Bot size={28} style={{ color: "var(--accent-blue)" }} />
            <h3 className="text-xl font-bold mt-4 mb-2">Digital FTE</h3>
            <p className="text-4xl font-black gradient-text mb-1">&lt;$1,000<span className="text-lg font-normal" style={{ color: "var(--text-secondary)" }}>/yr</span></p>
            <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>API costs only — no overhead</p>
            <ul className="flex flex-col gap-2.5 text-sm" style={{ color: "var(--text-secondary)" }}>
              {["24/7/365 availability", "Zero downtime", "Instant scalability", "Continuous improvement"].map((x, i) => (
                <li key={i} className="flex items-center gap-2"><CheckCircle2 size={14} style={{ color: "var(--accent-cyan)" }} /> {x}</li>
              ))}
            </ul>
            <Link href="/signup" className="mt-8 block text-center py-3 rounded-xl text-sm font-bold text-white animate-gradient" style={{ background: "var(--gradient-primary)" }}>
              Deploy Your AI Employee →
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─── CTA ─── */
function CTA() {
  return (
    <section className="py-24 px-6 relative overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full" style={{ background: "radial-gradient(circle, var(--glow-blue) 0%, transparent 70%)", opacity: 0.2 }} />
      </div>
      <div className="relative z-10 mx-auto max-w-3xl text-center">
        <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight mb-6">
          Ready to Hire Your <span className="gradient-text">AI Employee</span>?
        </h2>
        <p className="text-lg mb-8" style={{ color: "var(--text-secondary)" }}>
          Deploy a production-grade Customer Success FTE in minutes. Start handling support across all channels today.
        </p>
        <Link href="/signup" className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-base font-bold text-white glow-box animate-gradient" style={{ background: "var(--gradient-primary)" }}>
          Start Building Now <ArrowRight size={18} />
        </Link>
      </div>
    </section>
  );
}

/* ─── FOOTER ─── */
function Footer() {
  return (
    <footer className="py-12 px-6" style={{ borderTop: "1px solid var(--border-primary)", background: "var(--bg-secondary)" }}>
      <div className="mx-auto max-w-7xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
            <Bot size={14} className="text-white" />
          </div>
          <span className="text-sm font-bold gradient-text">AgentForge</span>
        </div>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>© 2026 AgentForge — Digital FTE Factory. Built for Hackathon V.</p>
        <div className="flex gap-6">
          {["Privacy", "Terms", "Docs"].map((l, i) => (
            <a key={i} href="#" className="text-xs transition-colors" style={{ color: "var(--text-muted)" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}>
              {l}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}

/* ─── PAGE ─── */
export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Channels />
      <Metrics />
      <TechStack />
      <Pricing />
      <CTA />
      <Footer />
    </>
  );
}

import { NextRequest, NextResponse } from "next/server";

// Simulated knowledge base for the agent
const knowledgeBase: Record<string, string> = {
    "api key": "To reset your API key: Go to Settings → API Keys → Generate New Key. Your old key will be deactivated for security.",
    "password": "To reset your password: Click 'Forgot Password' on the login page, enter your email, and follow the link sent to your inbox.",
    "export": "To export data: Navigate to Dashboard → Reports → Export. You can download data as CSV, JSON, or PDF format.",
    "login": "If you cannot log in: 1) Check your email and password 2) Clear browser cache 3) Try incognito mode 4) Reset password if needed.",
    "billing": "For billing inquiries, I'll connect you with our billing team. Please provide your account email for faster assistance.",
    "sso": "SSO setup: Go to Settings → Security → Single Sign-On. We support SAML 2.0, OAuth 2.0, and OpenID Connect protocols.",
    "integration": "For API integrations: Check our docs at /api/v1/docs. We support REST and GraphQL endpoints with OAuth2 authentication.",
    "notification": "To manage notifications: Go to Settings → Notifications. You can enable/disable email, SMS, and in-app notifications.",
    "dark mode": "Dark mode is available in Settings → Appearance → Theme. Select 'Dark' or 'System' to match your OS preference.",
    "pricing": "I'd be happy to connect you with our sales team for detailed pricing information. Let me escalate this for you.",
};

// Simple sentiment analysis
function analyzeSentiment(text: string): { score: number; label: string } {
    const negative = ["angry", "frustrated", "terrible", "broken", "worst", "hate", "ridiculous", "awful", "horrible"];
    const positive = ["thanks", "thank", "great", "amazing", "awesome", "love", "excellent", "wonderful", "perfect"];
    const lower = text.toLowerCase();

    let score = 0.5;
    negative.forEach((w) => { if (lower.includes(w)) score -= 0.15; });
    positive.forEach((w) => { if (lower.includes(w)) score += 0.1; });
    score = Math.max(0, Math.min(1, score));

    const label = score >= 0.6 ? "positive" : score >= 0.3 ? "neutral" : "negative";
    return { score, label };
}

// Search knowledge base
function searchKB(query: string): string {
    const lower = query.toLowerCase();
    for (const [key, value] of Object.entries(knowledgeBase)) {
        if (lower.includes(key)) return value;
    }
    return "I'll look into this and get back to you with more information. In the meantime, you can check our help center at /docs.";
}

// Check escalation
function shouldEscalate(text: string, sentimentScore: number): { escalate: boolean; reason: string } {
    const lower = text.toLowerCase();
    if (["price", "pricing", "cost", "quote"].some((w) => lower.includes(w)))
        return { escalate: true, reason: "pricing_inquiry" };
    if (["lawyer", "legal", "sue", "attorney"].some((w) => lower.includes(w)))
        return { escalate: true, reason: "legal_concern" };
    if (["refund", "money back", "chargeback"].some((w) => lower.includes(w)))
        return { escalate: true, reason: "refund_request" };
    if (["human", "agent", "representative", "person"].some((w) => lower.includes(w)))
        return { escalate: true, reason: "human_requested" };
    if (sentimentScore < 0.3) return { escalate: true, reason: "negative_sentiment" };
    return { escalate: false, reason: "" };
}

export async function POST(request: NextRequest) {
    try {
        const { message, channel = "web_form" } = await request.json();

        if (!message?.trim()) {
            return NextResponse.json({
                response: "Could you tell me more about what you need help with?",
                tools: [],
                sentiment: { score: 0.5, label: "neutral" },
                escalated: false,
            });
        }

        const apiKey = process.env.OPENAI_API_KEY;
        const baseUrl = process.env.OPENAI_BASE_URL || "https://api.cerebras.ai/v1";
        const model = process.env.CEREBRAS_MODEL || "llama3.1-70b";

        // Step 1: Real LLM call to Cerebras
        const response = await fetch(`${baseUrl}/chat/completions`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                model: model,
                messages: [
                    { role: "system", content: "You are a helpful Customer Success FTE agent. Answer as concisely as possible." },
                    { role: "user", content: message }
                ],
                temperature: 0.7,
                max_tokens: 500,
            }),
        });

        if (!response.ok) {
            throw new Error(`Cerebras API failed: ${response.statusText}`);
        }

        const result = await response.json();
        const aiResponse = result.choices[0].message.content;

        // Step 2: Analyze sentiment (simplified)
        const sentiment = analyzeSentiment(message);

        // Step 3: Check escalation
        const escalation = shouldEscalate(message, sentiment.score);

        const tools: string[] = ["create_ticket", "analyze_sentiment", "search_knowledge_base", "send_response"];

        if (escalation.escalate) {
            tools.push("escalate_to_human");
        }

        return NextResponse.json({
            response: aiResponse,
            tools,
            sentiment,
            escalated: escalation.escalate,
            channel,
            ticket_id: `TK-${Date.now().toString(36).toUpperCase()}`,
        });
    } catch (error: any) {
        console.error("Agent error:", error);
        return NextResponse.json(
            { error: "Agent processing failed", details: error.message },
            { status: 500 }
        );
    }
}

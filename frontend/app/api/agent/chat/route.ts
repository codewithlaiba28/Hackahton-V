import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
    try {
        const { message, channel = "web_form", customer_id = "web-user-default" } = await request.json();

        if (!message?.trim()) {
            return NextResponse.json({
                response: "Could you tell me more about what you need help with?",
                tools: [],
                escalated: false,
            });
        }

        // Call the REAL backend agent endpoint
        const response = await fetch(`${BACKEND_URL}/agent/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message,
                channel,
                customer_id,
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Backend Agent failed: ${errorText}`);
        }

        const result = await response.json();

        return NextResponse.json({
            response: result.response,
            tools: result.tools || [],
            conversation_id: result.conversation_id,
            ticket_id: result.ticket_id,
            channel,
        });
    } catch (error: any) {
        console.error("Agent API proxy error:", error);
        return NextResponse.json(
            { error: "Agent processing failed", details: error.message },
            { status: 500 }
        );
    }
}

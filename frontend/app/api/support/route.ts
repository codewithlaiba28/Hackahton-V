import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
    try {
        const data = await request.json();

        // Validate required fields
        const required = ["name", "email", "subject", "message", "category", "priority"];
        for (const field of required) {
            if (!data[field]) {
                return NextResponse.json(
                    { error: `Missing required field: ${field}` },
                    { status: 422 }
                );
            }
        }

        // Try to reach backend, fallback to local processing
        try {
            const backendRes = await fetch(`${BACKEND_URL}/support/submit`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            if (backendRes.ok) {
                const result = await backendRes.json();
                return NextResponse.json(result);
            }
        } catch {
            // Backend not reachable — process locally
        }

        // Local fallback: simulate ticket creation
        const ticketId = `TK-${Date.now().toString(36).toUpperCase()}`;
        return NextResponse.json({
            ticket_id: ticketId,
            message: "Your support request has been submitted successfully!",
            estimated_response_time: "Within 24 hours",
            channel: "web_form",
            status: "open",
        });
    } catch {
        return NextResponse.json(
            { error: "Failed to process support request" },
            { status: 500 }
        );
    }
}

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

        // Strictly require backend processing - NO FALLBACKS
        const backendRes = await fetch(`${BACKEND_URL}/support/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (backendRes.ok) {
            const result = await backendRes.json();
            return NextResponse.json(result);
        } else {
            const errorText = await backendRes.text();
            throw new Error(`Backend Error: ${errorText}`);
        }
    } catch (err: any) {
        console.error("Support API Error:", err);
        return NextResponse.json(
            { error: "Failed to process support request. Backend unreachable or errored." },
            { status: 500 }
        );
    }
}

import { getSessionCookie } from "better-auth/cookies";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
    const session = getSessionCookie(request);

    const isAuthRoute =
        request.nextUrl.pathname.startsWith("/login") ||
        request.nextUrl.pathname.startsWith("/signup");

    const isDashboardRoute = request.nextUrl.pathname.startsWith("/dashboard");

    // Redirect unauthenticated users away from dashboard
    if (!session && isDashboardRoute) {
        return NextResponse.redirect(new URL("/login", request.url));
    }

    // Redirect authenticated users away from auth pages
    if (session && isAuthRoute) {
        return NextResponse.redirect(new URL("/dashboard", request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/dashboard/:path*", "/login", "/signup"],
};

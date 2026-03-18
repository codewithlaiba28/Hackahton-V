---
name: better-auth
description: How to use Better Auth for authentication in Next.js with a PostgreSQL database
---

# Better Auth Integration Skill

## Overview
Better Auth is a modern, framework-agnostic authentication library that provides email/password, OAuth, and session management out of the box.

## Installation
```bash
npm install better-auth @better-auth/cli
```

## Server-Side Configuration (`lib/auth.ts`)
```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "pg",
    url: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,      // 1 day
  },
});
```

## API Route Handler (`app/api/auth/[...all]/route.ts`)
```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

## Client-Side Hooks (`lib/auth-client.ts`)
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

## Using in Components
```typescript
"use client";
import { signIn, signUp, signOut, useSession } from "@/lib/auth-client";

// Sign In
await signIn.email({ email, password });

// Sign Up
await signUp.email({ name, email, password });

// Sign Out
await signOut();

// Get Session (hook)
const { data: session, isPending } = useSession();
```

## Database Tables (auto-created by Better Auth)
- `user` — id, name, email, emailVerified, image, createdAt, updatedAt
- `session` — id, expiresAt, token, ipAddress, userAgent, userId
- `account` — id, accountId, providerId, userId, accessToken, refreshToken, etc.
- `verification` — id, identifier, value, expiresAt, createdAt, updatedAt

## Middleware Protection
```typescript
// middleware.ts
import { getSessionCookie } from "better-auth/cookies";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const session = getSessionCookie(request);
  if (!session && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*"] };
```

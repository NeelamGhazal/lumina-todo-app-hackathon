# NextAuth.js OAuth Authentication

Production-ready OAuth implementation for Next.js App Router.

## Quick Setup

### 1. Install Dependencies

```bash
npm install next-auth@beta
```

### 2. Create Auth Configuration

```typescript
// src/lib/auth.ts
import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
        token.provider = account?.provider;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
});
```

### 3. Create Route Handler

```typescript
// src/app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/lib/auth";

export const { GET, POST } = handlers;
```

### 4. Add Middleware

```typescript
// src/middleware.ts
import { auth } from "@/lib/auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isAuthPage = req.nextUrl.pathname.startsWith("/login");
  const isProtectedRoute = req.nextUrl.pathname.startsWith("/dashboard");

  if (isProtectedRoute && !isLoggedIn) {
    return Response.redirect(new URL("/login", req.url));
  }

  if (isAuthPage && isLoggedIn) {
    return Response.redirect(new URL("/dashboard", req.url));
  }
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

## Environment Variables

```bash
# .env.local
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-min-32-chars

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Generate Secret

```bash
openssl rand -base64 32
```

## Provider Configuration

### Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (dev)
   - `https://yourdomain.com/api/auth/callback/google` (prod)

### GitHub OAuth App

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Create new OAuth App
3. Set callback URL:
   - `http://localhost:3000/api/auth/callback/github` (dev)
   - `https://yourdomain.com/api/auth/callback/github` (prod)

## JWT vs Database Sessions

### JWT Sessions (Default)

```typescript
// Pros: Stateless, no database required, fast
// Cons: Cannot invalidate individual sessions

export const { auth } = NextAuth({
  session: { strategy: "jwt" },
  // ...
});
```

### Database Sessions

```typescript
// Pros: Can invalidate sessions, store more data
// Cons: Requires database, slower

import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma";

export const { auth } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: "database" },
  // ...
});
```

## Client Components

```typescript
"use client";

import { signIn, signOut, useSession } from "next-auth/react";

export function AuthButtons() {
  const { data: session, status } = useSession();

  if (status === "loading") return <div>Loading...</div>;

  if (session) {
    return (
      <div>
        <p>Signed in as {session.user?.email}</p>
        <button onClick={() => signOut()}>Sign out</button>
      </div>
    );
  }

  return (
    <div>
      <button onClick={() => signIn("google")}>Sign in with Google</button>
      <button onClick={() => signIn("github")}>Sign in with GitHub</button>
    </div>
  );
}
```

### Session Provider Setup

```typescript
// src/app/providers.tsx
"use client";

import { SessionProvider } from "next-auth/react";

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

## Server Components

```typescript
// No useSession hook - use auth() directly
import { auth } from "@/lib/auth";

export default async function Dashboard() {
  const session = await auth();

  if (!session) {
    redirect("/login");
  }

  return <div>Welcome, {session.user?.name}</div>;
}
```

## Common Mistakes & Solutions

### 1. NEXTAUTH_URL Not Set in Production

```bash
# Vercel auto-sets NEXTAUTH_URL, but verify:
NEXTAUTH_URL=https://yourdomain.com
```

### 2. Callback URL Mismatch

**Error:** `redirect_uri_mismatch`

**Fix:** Ensure callback URLs in provider console match exactly:
- Include `/api/auth/callback/[provider]`
- Match protocol (http vs https)
- No trailing slashes

### 3. Secret Not Set

**Error:** `NO_SECRET` or `JWE_DECRYPTION_FAILED`

**Fix:** Always set `NEXTAUTH_SECRET` in production:
```bash
NEXTAUTH_SECRET=$(openssl rand -base64 32)
```

### 4. TypeScript Session Types

```typescript
// src/types/next-auth.d.ts
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
    } & DefaultSession["user"];
  }
}
```

### 5. CORS Issues with API Routes

```typescript
// Ensure middleware doesn't block auth routes
export const config = {
  matcher: ["/((?!api/auth|_next/static|_next/image|favicon.ico).*)"],
};
```

## Best Practices

### Security

1. **Always use HTTPS in production**
2. **Rotate secrets periodically**
3. **Validate email domains for enterprise:**

```typescript
callbacks: {
  async signIn({ user, account }) {
    if (account?.provider === "google") {
      return user.email?.endsWith("@yourcompany.com") ?? false;
    }
    return true;
  },
}
```

### Performance

1. **Use JWT for stateless auth** (faster, no DB hit)
2. **Cache session in React Query/SWR** for client components
3. **Minimize data stored in token**

### User Experience

1. **Handle loading states** with skeleton UI
2. **Provide clear error messages** on auth failure
3. **Support account linking** for multiple providers

### Production Checklist

- [ ] NEXTAUTH_SECRET is set (32+ chars)
- [ ] NEXTAUTH_URL matches production domain
- [ ] Callback URLs configured in all providers
- [ ] HTTPS enabled
- [ ] Error page configured
- [ ] Session expiry set appropriately
- [ ] Rate limiting on auth endpoints

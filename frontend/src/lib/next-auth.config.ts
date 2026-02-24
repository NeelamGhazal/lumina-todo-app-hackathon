/**
 * NextAuth.js v5 Configuration for OAuth Social Login
 * Per specs/010-oauth-social-login/plan.md AD-001, AD-002
 *
 * Hybrid auth strategy:
 * - NextAuth.js handles OAuth flow (GitHub redirects and callbacks)
 * - After OAuth success, we call backend /api/auth/oauth endpoint
 * - Backend returns JWT which we store in existing cookie mechanism
 *
 * Note: Currently GitHub only. Google OAuth requires billing setup.
 */

import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { cookies } from "next/headers";
import type { NextAuthConfig } from "next-auth";

// Backend API URL for OAuth endpoint
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// Token cookie name - must match client.ts
const TOKEN_COOKIE_NAME = "auth_token";

/**
 * NextAuth.js configuration
 */
export const authConfig: NextAuthConfig = {
  // Only include GitHub provider if credentials are configured
  providers: (process.env.AUTH_GITHUB_ID && process.env.AUTH_GITHUB_SECRET)
    ? [
        GitHub({
          clientId: process.env.AUTH_GITHUB_ID,
          clientSecret: process.env.AUTH_GITHUB_SECRET,
        }),
      ]
    : [],

  // Use JWT strategy (no database sessions)
  session: {
    strategy: "jwt",
  },

  // Custom pages - use our existing login page
  pages: {
    signIn: "/login",
    error: "/login",
  },

  callbacks: {
    /**
     * signIn callback - called after successful OAuth authentication
     * Calls backend to create/link user and get JWT
     */
    async signIn({ user, account, profile }) {
      if (!account || !user.email) {
        return false;
      }

      // Only process OAuth sign-ins (not credentials)
      if (account.type !== "oauth" && account.type !== "oidc") {
        return true;
      }

      try {
        // Call backend to create/link user and get JWT
        const response = await fetch(`${API_URL}/auth/oauth`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            provider: account.provider,
            provider_id: account.providerAccountId,
            email: user.email,
            name: user.name || profile?.name,
            image_url: user.image || null,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          console.error("Backend OAuth error:", error);
          return false;
        }

        const data = await response.json();

        // Store the backend JWT token, user info, and provider in the account object
        // This will be available in the jwt callback
        (account as { backendToken?: string; backendUserId?: string; oauthProvider?: string }).backendToken = data.access_token;
        (account as { backendUserId?: string }).backendUserId = data.user.id;
        (account as { oauthProvider?: string }).oauthProvider = account.provider;

        return true;
      } catch (error) {
        console.error("OAuth backend sync error:", error);
        return false;
      }
    },

    /**
     * jwt callback - called when JWT is created/updated
     * Stores backend token in the JWT and sets auth_token cookie
     */
    async jwt({ token, account, user }) {
      // On initial sign in, add backend token to JWT and set cookie
      if (account) {
        const extendedAccount = account as {
          backendToken?: string;
          backendUserId?: string;
          oauthProvider?: string;
        };
        if (extendedAccount.backendToken) {
          token.backendToken = extendedAccount.backendToken;
          token.backendUserId = extendedAccount.backendUserId;
          token.oauthProvider = extendedAccount.oauthProvider;

          // Set auth_token cookie server-side for immediate availability
          // This ensures the cookie is set before redirect to /tasks
          try {
            const cookieStore = await cookies();
            cookieStore.set(TOKEN_COOKIE_NAME, extendedAccount.backendToken, {
              path: "/",
              maxAge: 60 * 60 * 24, // 24 hours
              sameSite: "lax",
              httpOnly: false, // Must be accessible by client JS
            });
          } catch (error) {
            // cookies() might not be available in all contexts
            console.log("Could not set cookie server-side:", error);
          }
        }
      }
      return token;
    },

    /**
     * session callback - called when session is checked
     * Exposes backend token and OAuth provider to client
     */
    async session({ session, token }) {
      // Add backend token and provider to session for client access
      if (token.backendToken) {
        (session as { backendToken?: string }).backendToken = token.backendToken as string;
      }
      if (token.backendUserId) {
        session.user.id = token.backendUserId as string;
      }
      if (token.oauthProvider) {
        (session as { oauthProvider?: string }).oauthProvider = token.oauthProvider as string;
      }
      return session;
    },

    /**
     * redirect callback - handle post-auth redirects
     */
    async redirect({ url, baseUrl }) {
      // After successful OAuth, redirect to tasks dashboard
      if (url.startsWith(baseUrl)) {
        return url;
      }
      // Default to tasks page after OAuth
      return `${baseUrl}/tasks`;
    },
  },

  // Events for logging/debugging
  events: {
    async signIn({ user, account }) {
      console.log(`OAuth sign in: ${user.email} via ${account?.provider}`);
    },
    async signOut() {
      console.log("OAuth sign out");
    },
  },

  // Enable debug in development
  debug: process.env.NODE_ENV === "development",
};

// Export NextAuth handlers and utilities
export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);

// Re-export for convenience
export { auth as getServerSession };

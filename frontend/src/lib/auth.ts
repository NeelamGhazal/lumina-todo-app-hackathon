/**
 * Better Auth Client Configuration
 * Based on specs/002-phase2-todo-frontend/plan.md ADR-006
 */

import { createAuthClient } from "better-auth/react";

/**
 * Better Auth client instance
 * Handles authentication state and operations
 */
export const authClient = createAuthClient({
  baseURL:
    process.env.BETTER_AUTH_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:3000",
});

/**
 * Auth hooks and utilities
 */
export const {
  useSession,
  signIn,
  signUp,
  signOut,
  getSession,
} = authClient;

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const session = await getSession();
    return !!session?.data?.user;
  } catch {
    return false;
  }
}

/**
 * Get current user from session
 */
export async function getCurrentUser() {
  try {
    const session = await getSession();
    return session?.data?.user ?? null;
  } catch {
    return null;
  }
}

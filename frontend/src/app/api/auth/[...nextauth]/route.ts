/**
 * NextAuth.js v5 Route Handler
 * Per specs/010-oauth-social-login/tasks.md T010
 *
 * Handles OAuth callbacks for Google and GitHub providers.
 * Callback URLs configured in OAuth apps:
 * - Google: http://localhost:3000/api/auth/callback/google
 * - GitHub: http://localhost:3000/api/auth/callback/github
 */

import { handlers } from "@/lib/next-auth.config";

// Export GET and POST handlers for NextAuth
export const { GET, POST } = handlers;

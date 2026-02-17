"use client";

import { useEffect } from "react";
import { useSession } from "next-auth/react";
import { setAuthToken } from "@/lib/api/client";

/**
 * OAuthSessionSync - Syncs NextAuth session's backend token to existing cookie storage
 * Per specs/010-oauth-social-login/plan.md AD-002 (Hybrid Auth Strategy)
 *
 * After OAuth success, NextAuth's signIn callback fetches a JWT from our backend.
 * This component syncs that token to the existing auth_token cookie so the
 * apiClient can use it for authenticated API calls.
 */
export function OAuthSessionSync() {
  const { data: session } = useSession();

  useEffect(() => {
    // When session contains a backend token, sync it to the cookie
    const extendedSession = session as { backendToken?: string } | null;
    if (extendedSession?.backendToken) {
      setAuthToken(extendedSession.backendToken);
    }
  }, [session]);

  // This component doesn't render anything
  return null;
}

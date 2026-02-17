/**
 * NextAuth.js v5 Type Extensions
 * Per specs/010-oauth-social-login/tasks.md T011
 *
 * Extends NextAuth types to include backend JWT token
 * and custom user properties from our OAuth flow.
 */

import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  /**
   * Extended Session interface
   * Includes backend JWT for API calls
   */
  interface Session {
    /** Backend JWT token for FastAPI calls */
    backendToken?: string;
    /** OAuth provider if user signed in via OAuth (google/github) */
    oauthProvider?: string;
    user: {
      /** User ID from backend */
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }

  /**
   * Extended User interface
   */
  interface User {
    id?: string;
    name?: string | null;
    email?: string | null;
    image?: string | null;
  }
}

declare module "next-auth/jwt" {
  /**
   * Extended JWT interface
   * Stores backend token for persistence across requests
   */
  interface JWT {
    /** Backend JWT token */
    backendToken?: string;
    /** Backend user ID */
    backendUserId?: string;
    /** OAuth provider (google/github) */
    oauthProvider?: string;
  }
}

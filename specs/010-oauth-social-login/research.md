# Research: OAuth Social Login

**Feature**: 010-oauth-social-login
**Date**: 2026-02-13
**Purpose**: Resolve technical unknowns before implementation

## Research Topics

### 1. NextAuth.js v5 with App Router

**Decision**: Use NextAuth.js v5 (Auth.js) with App Router route handlers

**Rationale**:
- NextAuth.js v5 is the current stable version designed for Next.js App Router
- Built-in support for Google and GitHub providers
- JWT session strategy eliminates need for session database
- CSRF protection and state parameter handling built-in

**Key Configuration**:
```typescript
// frontend/src/lib/auth.ts
import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import GitHub from "next-auth/providers/github"

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
  session: { strategy: "jwt" },
  callbacks: {
    async signIn({ user, account }) {
      // Call backend to create/link user
      return true
    },
    async jwt({ token, user, account }) {
      // Add backend JWT to token
      return token
    },
    async session({ session, token }) {
      // Expose backend JWT in session
      return session
    },
  },
})
```

**Alternatives Considered**:
- Better Auth: Constitution default, but lacks NextAuth's OAuth maturity
- Direct OAuth: Too complex, security risks

### 2. OAuth Provider Setup

**Decision**: Google Cloud Console + GitHub OAuth Apps

**Google OAuth Setup**:
1. Go to Google Cloud Console > APIs & Services > Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`
4. Copy Client ID and Client Secret

**GitHub OAuth Setup**:
1. Go to GitHub Settings > Developer Settings > OAuth Apps
2. Create new OAuth App
3. Authorization callback URL: `http://localhost:3000/api/auth/callback/github`
4. Copy Client ID and Client Secret

**Environment Variables**:
```env
# Frontend (.env.local)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
NEXTAUTH_SECRET=random-32-char-secret
NEXTAUTH_URL=http://localhost:3000

# Backend (.env) - Only if backend validates OAuth tokens
# For this implementation, backend receives profile data, not raw tokens
```

### 3. Backend Integration Strategy

**Decision**: Hybrid approach - NextAuth handles OAuth, backend issues JWTs

**Flow**:
1. User clicks OAuth button → NextAuth redirects to provider
2. Provider callback → NextAuth receives profile (email, name, provider_id)
3. NextAuth `signIn` callback → POST to backend `/api/auth/oauth`
4. Backend creates/links user → returns JWT
5. NextAuth stores JWT in session → frontend uses for API calls

**Backend Endpoint**:
```python
# POST /api/auth/oauth
{
  "provider": "google" | "github",
  "provider_id": "oauth-user-id",
  "email": "user@example.com",
  "name": "User Name"
}

# Response
{
  "access_token": "jwt-token",
  "user": { "id", "email", "name" }
}
```

**Rationale**:
- Backend remains single source of truth
- Existing JWT infrastructure reused
- No changes to existing API authentication

### 4. User Model Extensions

**Decision**: Add OAuth fields to existing User model

**New Fields**:
```python
class User(SQLModel, table=True):
    # Existing fields...
    hashed_password: str | None = Field(default=None, max_length=255)  # Now nullable

    # OAuth fields
    oauth_provider: str | None = Field(default=None, max_length=50)  # 'google', 'github'
    oauth_provider_id: str | None = Field(default=None, max_length=255)

    # Optional: profile image from OAuth
    image_url: str | None = Field(default=None, max_length=500)
```

**Multi-Provider Support**:
For users linking multiple providers, we store the most recent provider. The email remains the primary identifier for account linking.

### 5. Account Linking Logic

**Decision**: Auto-link by email match (per spec clarification)

**Algorithm**:
```python
async def oauth_login(provider, provider_id, email, name):
    # 1. Check if user exists by email
    user = await get_user_by_email(email)

    if user:
        # 2a. Link OAuth to existing account
        user.oauth_provider = provider
        user.oauth_provider_id = provider_id
        if name and not user.name:
            user.name = name
    else:
        # 2b. Create new user (no password)
        user = User(
            email=email,
            name=name,
            hashed_password=None,  # OAuth-only user
            oauth_provider=provider,
            oauth_provider_id=provider_id,
        )

    await save(user)
    return create_jwt(user.id)
```

### 6. OAuth Button Design

**Decision**: Match existing Lumina design system

**Button Specifications**:
- Full-width buttons matching existing auth form width
- Provider logos (Google G, GitHub Octocat)
- Text: "Continue with Google", "Continue with GitHub"
- Loading state: Spinner inside button, button disabled
- Colors: Subtle backgrounds that complement Lumina purple theme

**Component Structure**:
```tsx
<OAuthButtons
  onGoogleClick={() => signIn("google")}
  onGitHubClick={() => signIn("github")}
  isLoading={isLoading}
  loadingProvider={loadingProvider}
/>
```

### 7. Error Handling

**Decision**: User-friendly error messages for all OAuth failures

**Error Scenarios**:
| Scenario | User Message |
|----------|--------------|
| User cancels OAuth | "Login cancelled. You can try again anytime." |
| Provider error | "Unable to connect to {provider}. Please try again." |
| Network error | "Connection failed. Please check your internet and try again." |
| Backend error | "Something went wrong. Please try again later." |
| No email from provider | "We couldn't get your email from {provider}. Please try another method." |

### 8. Security Considerations

**Implemented by NextAuth.js**:
- CSRF protection via state parameter
- Secure cookie settings (httpOnly, sameSite)
- Token encryption

**Implemented by Backend**:
- Email verification assumed (OAuth providers verify)
- JWT signing with existing secret
- No raw OAuth tokens stored (only provider_id)

**Environment Security**:
- All secrets in environment variables
- `.env.local` gitignored
- Production secrets via deployment platform

## Summary

All research topics resolved. Key findings:

1. **NextAuth.js v5** with JWT strategy is the right choice
2. **Hybrid auth** maintains existing system while adding OAuth
3. **Auto-link by email** is safe since OAuth providers verify emails
4. **5 environment variables** needed for frontend OAuth
5. **User model** needs 3 new nullable fields
6. **Backend endpoint** `/api/auth/oauth` creates/links users

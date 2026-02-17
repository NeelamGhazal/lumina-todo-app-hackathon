# Quickstart: OAuth Social Login

**Feature**: 010-oauth-social-login
**Time to Setup**: ~15 minutes

## Prerequisites

- Evolution-Todo backend running (`uv run uvicorn app.main:app`)
- Evolution-Todo frontend running (`npm run dev`)
- Google Cloud Console access
- GitHub account with Developer settings access

## Step 1: Google OAuth App Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth client ID**
5. Select **Web application**
6. Configure:
   - **Name**: Evolution-Todo Local
   - **Authorized JavaScript origins**: `http://localhost:3000`
   - **Authorized redirect URIs**: `http://localhost:3000/api/auth/callback/google`
7. Click **Create**
8. Copy **Client ID** and **Client Secret**

## Step 2: GitHub OAuth App Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps > New OAuth App**
3. Configure:
   - **Application name**: Evolution-Todo Local
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Click **Register application**
5. Copy **Client ID**
6. Click **Generate a new client secret**
7. Copy **Client Secret**

## Step 3: Configure Frontend Environment

Create or update `frontend/.env.local`:

```env
# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GITHUB_CLIENT_ID=your-github-client-id-here
GITHUB_CLIENT_SECRET=your-github-client-secret-here

# NextAuth.js
NEXTAUTH_SECRET=generate-a-32-char-random-string
NEXTAUTH_URL=http://localhost:3000

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Generate NEXTAUTH_SECRET**:
```bash
openssl rand -base64 32
```

## Step 4: Verify Backend Compatibility

The backend needs the OAuth endpoint. Check that migrations are applied:

```bash
cd api
uv run uvicorn app.main:app --reload
```

The `/api/auth/oauth` endpoint should be available after implementation.

## Step 5: Test OAuth Flow

1. Start both servers:
   ```bash
   # Terminal 1: Backend
   cd api && uv run uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. Open `http://localhost:3000/login`

3. Click **Continue with Google**:
   - Should redirect to Google consent screen
   - After authorization, should redirect back to tasks dashboard
   - Check that user appears in database

4. Click **Continue with GitHub**:
   - Should redirect to GitHub authorization
   - After authorization, should redirect back to tasks dashboard
   - Check that user appears in database

## Verification Checklist

- [ ] Google OAuth redirects correctly
- [ ] Google OAuth creates new user in database
- [ ] GitHub OAuth redirects correctly
- [ ] GitHub OAuth creates new user in database
- [ ] Existing user (email match) gets OAuth linked
- [ ] OAuth user can access all features
- [ ] Logout works for OAuth users
- [ ] Re-login with OAuth works without re-authorization

## Troubleshooting

### "redirect_uri_mismatch" Error

- Verify callback URLs match exactly in provider settings
- Google: `http://localhost:3000/api/auth/callback/google`
- GitHub: `http://localhost:3000/api/auth/callback/github`

### "Invalid client" Error

- Double-check Client ID and Client Secret in `.env.local`
- Ensure no trailing spaces or newlines

### OAuth Callback Fails

- Check browser console for errors
- Verify `NEXTAUTH_URL` matches your local URL
- Check backend logs for `/api/auth/oauth` errors

### User Not Created

- Check backend logs for database errors
- Verify SQLite file is writable
- Check User model has nullable `hashed_password`

## Production Setup

For production deployment, update:

1. **Google Cloud Console**:
   - Add production domain to authorized origins
   - Add production callback URL

2. **GitHub OAuth App**:
   - Update callback URL to production domain

3. **Environment Variables**:
   ```env
   NEXTAUTH_URL=https://your-domain.com
   # Use production-grade secrets
   ```

## Related Files

- `frontend/src/lib/auth.ts` - NextAuth.js configuration
- `frontend/src/app/api/auth/[...nextauth]/route.ts` - NextAuth route handler
- `frontend/src/components/auth/oauth-buttons.tsx` - OAuth button components
- `api/app/routers/auth.py` - Backend OAuth endpoint
- `api/app/models/user.py` - User model with OAuth fields

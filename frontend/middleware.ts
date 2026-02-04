import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Protected routes that require authentication
 */
const protectedRoutes = ["/tasks", "/dashboard"];

/**
 * Auth routes (login/signup)
 */
const authRoutes = ["/login", "/signup"];

/**
 * Auth middleware for protected routes.
 * Checks for auth_token cookie set by the frontend after login/register.
 *
 * FLOW:
 * - Landing page (/) is always accessible - shows Sign In / Sign Up buttons
 * - /tasks requires authentication - redirects to /login if not authenticated
 * - /login and /signup redirect to /tasks if already authenticated
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for auth token cookie (set by frontend after login/register)
  const authToken = request.cookies.get("auth_token")?.value;
  const hasSession = !!authToken;

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some(
    (route) => pathname.startsWith(route)
  );

  // Check if route is an auth route (login/signup)
  const isAuthRoute = authRoutes.includes(pathname);

  // Redirect unauthenticated users from protected routes to login
  if (isProtectedRoute && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users from auth routes (login/signup) to tasks
  if (isAuthRoute && hasSession) {
    return NextResponse.redirect(new URL("/tasks", request.url));
  }

  // Landing page (/) is always accessible - no redirect
  // Users see the landing page with Sign In / Sign Up buttons

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};

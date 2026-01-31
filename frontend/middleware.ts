import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/auth/service(.*)",
  "/auth/gov(.*)",
  "/auth/admin(.*)",
  "/service(.*)", // Service routes are public (checked client-side via localStorage)
]);

const isGovRoute = createRouteMatcher(["/gov(.*)"]);
const isAdminRoute = createRouteMatcher(["/admin(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  // Allow public routes (including service)
  if (isPublicRoute(req)) {
    return NextResponse.next();
  }

  const { userId } = await auth();

  // If not signed in with Clerk, redirect to appropriate login page
  if (!userId) {
    if (isGovRoute(req)) {
      return NextResponse.redirect(new URL("/auth/gov", req.url));
    }
    if (isAdminRoute(req)) {
      return NextResponse.redirect(new URL("/auth/admin", req.url));
    }
    return NextResponse.redirect(new URL("/", req.url));
  }

  // Role-based access control is handled client-side by the dashboard pages
  // They check user.publicMetadata.role and redirect if needed

  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};

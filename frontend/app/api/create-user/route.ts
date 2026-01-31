import { clerkClient, auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    // Verify the requester is an admin
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const clerk = await clerkClient();
    const requestingUser = await clerk.users.getUser(userId);
    if (requestingUser.publicMetadata?.role !== "admin") {
      return NextResponse.json({ error: "Forbidden - Admin access required" }, { status: 403 });
    }

    const body = await request.json();
    const { email, password, role, firstName, lastName } = body;

    if (!email || !password || !role) {
      return NextResponse.json(
        { error: "Email, password, and role are required" },
        { status: 400 }
      );
    }

    if (!["gov", "admin"].includes(role)) {
      return NextResponse.json(
        { error: "Invalid role. Must be gov or admin" },
        { status: 400 }
      );
    }

    // Create user with Clerk
    const newUser = await clerk.users.createUser({
      emailAddress: [email],
      password,
      firstName: firstName || undefined,
      lastName: lastName || undefined,
      publicMetadata: {
        role,
      },
    });

    return NextResponse.json({
      success: true,
      user: {
        id: newUser.id,
        email: newUser.emailAddresses[0]?.emailAddress,
        role: newUser.publicMetadata?.role,
        firstName: newUser.firstName,
        lastName: newUser.lastName,
      },
    });
  } catch (error: unknown) {
    console.error("Error creating user:", error);
    
    // Handle Clerk-specific errors
    if (error && typeof error === "object" && "errors" in error) {
      const clerkError = error as { errors: Array<{ message: string }> };
      return NextResponse.json(
        { error: clerkError.errors[0]?.message || "Failed to create user" },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: "Failed to create user" },
      { status: 500 }
    );
  }
}

import { auth } from "@clerk/nextjs/server";
import { clerkClient } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import { randomBytes } from "crypto";

export async function POST() {
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

    // Generate a secure random token
    const token = `m2m_${randomBytes(32).toString("hex")}`;
    
    // Calculate expiry date (365 days from now)
    const validityDays = 365;
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + validityDays);

    // In a real implementation, you would store this token in a database
    // For now, we'll just return it
    // TODO: Store token hash in database for validation

    return NextResponse.json({
      success: true,
      token,
      expiresAt: expiresAt.toISOString(),
      validityDays,
    });
  } catch (error: unknown) {
    console.error("Error creating M2M token:", error);
    return NextResponse.json(
      { error: "Failed to create M2M token" },
      { status: 500 }
    );
  }
}

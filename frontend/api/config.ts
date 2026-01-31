/**
 * Centralized API configuration
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get the current auth token based on context
 * - Service dashboard: uses M2M token from localStorage
 * - Gov/Admin dashboard: uses Clerk JWT (passed explicitly)
 */
export const getAuthToken = (): string | null => {
  // Check for service M2M token first (stored during service auth)
  if (typeof window !== "undefined") {
    const serviceToken = localStorage.getItem("service_token");
    if (serviceToken) {
      return serviceToken;
    }
  }
  return null;
};

/**
 * Create headers for API requests
 * Automatically includes auth token if available
 */
export const getHeaders = (contentType?: string): HeadersInit => {
  const headers: HeadersInit = {};

  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  // Add auth token if available
  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Create headers with explicit Clerk JWT token
 * Used by gov/admin dashboards with Clerk authentication
 */
export const getHeadersWithClerkToken = (
  clerkToken: string,
  contentType?: string
): HeadersInit => {
  const headers: HeadersInit = {};

  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  headers["Authorization"] = `Bearer ${clerkToken}`;

  return headers;
};

/**
 * Helper to build full API URL
 */
export const apiUrl = (path: string): string => {
  return `${API_BASE_URL}${path}`;
};

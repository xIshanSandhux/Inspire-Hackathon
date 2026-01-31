"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { API_BASE_URL } from "@/api/config";

export default function ServiceAuthPage() {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!token || token.trim().length === 0) {
        throw new Error("Token is required");
      }

      // Validate the token against the backend
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token.trim()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to validate token");
      }

      const data = await response.json();

      if (!data.valid) {
        throw new Error("Invalid token");
      }

      if (data.user_type !== "service") {
        throw new Error("This token is not a service token");
      }

      // Token is valid - store authentication in localStorage
      localStorage.setItem("service_auth", "authenticated");
      localStorage.setItem("service_token", token.trim());

      // Redirect to service dashboard on success
      router.push("/service/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Service Authentication
          </CardTitle>
          <CardDescription className="text-center">
            Enter your M2M token to authenticate
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="mb-4">
            <Input
              id="token"
              type="password"
              placeholder="Enter your M2M token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
            />
            {error && (
              <p className="text-sm text-destructive text-center">{error}</p>
            )}
          </CardContent>
          <CardFooter>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Authenticating..." : "Authenticate"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

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
      // Simple token validation - you can add your own logic here
      if (!token || token.trim().length === 0) {
        throw new Error("Token is required");
      }

      // Store authentication in localStorage
      localStorage.setItem("service_auth", "authenticated");
      localStorage.setItem("service_token", token);

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

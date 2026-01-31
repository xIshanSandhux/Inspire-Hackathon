"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser, useAuth, SignOutButton } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FingerprintScanner } from "@/components/fingerprint-scanner";
import { PersonInfoDisplay } from "@/components/person-info-display";
import { CreateUserForm } from "@/components/create-user-form";
import { CreateM2MTokenForm } from "@/components/create-m2m-token-form";
import { useUserInfo, type UserInfoResponse } from "@/api/useIdentity";

type Tab = "users" | "tokens" | "lookup";
type LookupStep = "scanning" | "loading" | "display";

export default function AdminDashboard() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>("users");
  const [lookupStep, setLookupStep] = useState<LookupStep>("scanning");
  const [isScanning, setIsScanning] = useState(false);
  const [citizenInfo, setCitizenInfo] = useState<UserInfoResponse | null>(null);

  const userInfoMutation = useUserInfo();

  const role = user?.publicMetadata?.role as string | undefined;

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/auth/admin");
      } else if (role !== "admin") {
        router.push("/auth/admin");
      }
    }
  }, [isLoaded, user, role, router]);

  const handleScanComplete = async (fingerprintId: string) => {
    setIsScanning(false);
    setLookupStep("loading");

    try {
      // Get Clerk JWT token for authentication
      const clerkToken = await getToken();
      const result = await userInfoMutation.mutateAsync({
        fingerprintHash: fingerprintId,
        clerkToken: clerkToken || undefined,
      });
      setCitizenInfo(result);
      setLookupStep("display");
    } catch (error) {
      console.error("Failed to fetch citizen info:", error);
      setLookupStep("scanning");
    }
  };

  const handleScanAnother = () => {
    setCitizenInfo(null);
    setLookupStep("scanning");
  };

  if (!isLoaded || !user || role !== "admin") {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold">Admin Dashboard</h1>
            <p className="text-sm text-muted-foreground">System Administration</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">
                {user.firstName} {user.lastName}
              </p>
              <p className="text-xs text-muted-foreground">
                {user.emailAddresses[0]?.emailAddress}
              </p>
            </div>
            <SignOutButton>
              <Button variant="outline" size="sm">Sign Out</Button>
            </SignOutButton>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b">
        <div className="max-w-6xl mx-auto px-6">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab("users")}
              className={`py-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "users"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              User Management
            </button>
            <button
              onClick={() => setActiveTab("tokens")}
              className={`py-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "tokens"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              M2M Tokens
            </button>
            <button
              onClick={() => setActiveTab("lookup")}
              className={`py-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "lookup"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Citizen Lookup
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {activeTab === "users" && (
            <motion.div
              key="users"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid gap-6 lg:grid-cols-2"
            >
              <CreateUserForm />
              
              <Card>
                <CardHeader>
                  <CardTitle>User Management Overview</CardTitle>
                  <CardDescription>
                    System administration capabilities
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    As an administrator, you can create new users with specific roles:
                  </p>
                  <ul className="text-sm space-y-2">
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-blue-500" />
                      <span><strong>Government</strong> - Access to citizen verification portal</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-red-500" />
                      <span><strong>Admin</strong> - Full system access and user management</span>
                    </li>
                  </ul>
                  <p className="text-xs text-muted-foreground pt-2">
                    Note: Service providers use M2M tokens for authentication.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab === "tokens" && (
            <motion.div
              key="tokens"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid gap-6 lg:grid-cols-2"
            >
              <CreateM2MTokenForm />
              
              <Card>
                <CardHeader>
                  <CardTitle>About M2M Tokens</CardTitle>
                  <CardDescription>
                    Machine-to-Machine authentication
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    M2M tokens allow service providers to authenticate with the identity verification system without user interaction.
                  </p>
                  <ul className="text-sm space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Each token is valid for <strong>365 days</strong></span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Tokens are shown <strong>only once</strong> upon creation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Store tokens securely - they cannot be retrieved later</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Use tokens in the Authorization header as Bearer tokens</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab === "lookup" && (
            <motion.div
              key="lookup"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <AnimatePresence mode="wait">
                {lookupStep === "scanning" && (
                  <motion.div
                    key="scanning"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="flex flex-col items-center justify-center min-h-[60vh]"
                  >
                    <Card className="w-full max-w-md">
                      <CardHeader className="text-center">
                        <CardTitle>Citizen Lookup</CardTitle>
                        <CardDescription>
                          Scan fingerprint to retrieve citizen identity information
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="py-8">
                        <FingerprintScanner
                          onScanComplete={handleScanComplete}
                          isScanning={isScanning}
                          setIsScanning={setIsScanning}
                        />
                      </CardContent>
                    </Card>
                  </motion.div>
                )}

                {lookupStep === "loading" && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center justify-center min-h-[60vh] gap-4"
                  >
                    <motion.div
                      className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                    <p className="text-muted-foreground">Fetching citizen information...</p>
                  </motion.div>
                )}

                {lookupStep === "display" && citizenInfo && (
                  <motion.div
                    key="display"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="flex justify-center py-8"
                  >
                    <PersonInfoDisplay
                      userInfo={citizenInfo}
                      onScanAnother={handleScanAnother}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

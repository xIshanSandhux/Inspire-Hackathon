"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser, SignOutButton } from "@clerk/nextjs";
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
import { useUserInfo, type UserInfoResponse } from "@/api/useIdentity";

type FlowStep = "scanning" | "loading" | "display";

export default function GovDashboard() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const [flowStep, setFlowStep] = useState<FlowStep>("scanning");
  const [isScanning, setIsScanning] = useState(false);
  const [personInfo, setPersonInfo] = useState<UserInfoResponse | null>(null);

  const userInfoMutation = useUserInfo();

  const role = user?.publicMetadata?.role as string | undefined;

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/auth/gov");
      } else if (role !== "gov") {
        router.push("/auth/gov");
      }
    }
  }, [isLoaded, user, role, router]);

  const handleScanComplete = async (fingerprintId: string) => {
    setIsScanning(false);
    setFlowStep("loading");

    try {
      const result = await userInfoMutation.mutateAsync(fingerprintId);
      setPersonInfo(result);
      setFlowStep("display");
    } catch (error) {
      console.error("Failed to fetch citizen info:", error);
      setFlowStep("scanning");
    }
  };

  const handleScanAnother = () => {
    setPersonInfo(null);
    setFlowStep("scanning");
  };

  if (!isLoaded || !user || role !== "gov") {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold">Government Portal</h1>
            <p className="text-sm text-muted-foreground">Identity Verification System</p>
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

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {flowStep === "scanning" && (
            <motion.div
              key="scanning"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center justify-center min-h-[60vh]"
            >
              <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                  <CardTitle>Citizen Verification</CardTitle>
                  <CardDescription>
                    Scan citizen&apos;s fingerprint to retrieve their identity information
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

          {flowStep === "loading" && (
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

          {flowStep === "display" && personInfo && (
            <motion.div
              key="display"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex justify-center py-8"
            >
              <PersonInfoDisplay
                userInfo={personInfo}
                onScanAnother={handleScanAnother}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

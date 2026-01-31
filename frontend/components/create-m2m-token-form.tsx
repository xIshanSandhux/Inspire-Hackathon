"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCreateM2MToken } from "@/api/useAuth";

export function CreateM2MTokenForm() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tokenData, setTokenData] = useState<{
    token: string;
    expiresAt: string | null;
  } | null>(null);
  const [copied, setCopied] = useState(false);

  const createTokenMutation = useCreateM2MToken();

  const handleCreateToken = async () => {
    try {
      const result = await createTokenMutation.mutateAsync();
      setTokenData({
        token: result.token,
        expiresAt: result.expires_at,
      });
      setDialogOpen(true);
    } catch {
      // Error is handled by mutation
    }
  };

  const handleCopy = async () => {
    if (tokenData?.token) {
      await navigator.clipboard.writeText(tokenData.token);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setTokenData(null);
    setCopied(false);
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Create M2M Token</CardTitle>
          <CardDescription>
            Generate a new Machine-to-Machine token for service providers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            M2M tokens are used by service providers to authenticate with the identity
            verification system. Each token is valid for 365 days.
          </p>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <p className="text-sm text-amber-600 dark:text-amber-400">
              ⚠️ The token will only be shown once. Make sure to copy and store it securely.
            </p>
          </div>

          {createTokenMutation.error && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-destructive"
            >
              {createTokenMutation.error.message}
            </motion.p>
          )}

          <Button
            onClick={handleCreateToken}
            disabled={createTokenMutation.isPending}
            className="w-full"
          >
            {createTokenMutation.isPending ? "Generating..." : "Generate New Token"}
          </Button>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={handleCloseDialog}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <span className="text-green-500">✓</span> Token Generated
            </DialogTitle>
            <DialogDescription>
              Copy this token now. It will not be shown again.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Token</label>
              <div className="relative">
                <div className="bg-muted rounded-lg p-3 pr-20 font-mono text-xs break-all">
                  {tokenData?.token}
                </div>
                <Button
                  size="sm"
                  variant={copied ? "default" : "secondary"}
                  className="absolute right-2 top-1/2 -translate-y-1/2"
                  onClick={handleCopy}
                >
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Valid For</p>
                <p className="font-medium">365 days</p>
              </div>
              <div>
                <p className="text-muted-foreground">Expires</p>
                <p className="font-medium">
                  {tokenData?.expiresAt
                    ? new Date(tokenData.expiresAt).toLocaleDateString()
                    : "-"}
                </p>
              </div>
            </div>

            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
              <p className="text-sm text-destructive">
                ⚠️ This token will never be shown again. Make sure you have copied it before closing this dialog.
              </p>
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleCloseDialog}>
              I&apos;ve Copied the Token
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

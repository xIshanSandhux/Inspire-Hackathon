"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Document } from "@/api/useIdentity";

interface ExtractedInfoDisplayProps {
  documentType: "PASSPORT" | "BCID";
  document: Document;
  onComplete: () => void;
}

export function ExtractedInfoDisplay({
  documentType,
  document,
  onComplete,
}: ExtractedInfoDisplayProps) {
  const [countdown, setCountdown] = useState(30);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", delay: 0.2 }}
        className="flex justify-center"
      >
        <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-4xl"
          >
            ✓
          </motion.span>
        </div>
      </motion.div>

      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">Document Verified!</h2>
        <p className="text-muted-foreground">
          Your {documentType === "PASSPORT" ? "Passport" : "BC ID"} has been
          successfully processed
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {documentType === "PASSPORT" ? "🛂 Passport" : "🪪 BC ID"} Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Document ID</span>
            <span className="font-mono">{document.id}</span>
          </div>
          {Object.entries(document.metadata).map(([key, value]) => (
            <div key={key} className="flex justify-between text-sm">
              <span className="text-muted-foreground">
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </span>
              <span>{value}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="text-center space-y-3">
        <p className="text-lg font-medium text-green-600">Thank you!</p>
        <p className="text-sm text-muted-foreground">
          Returning to scanner in {countdown} seconds...
        </p>
        <div className="w-full bg-muted rounded-full h-1 overflow-hidden">
          <motion.div
            className="h-full bg-primary"
            initial={{ width: "100%" }}
            animate={{ width: "0%" }}
            transition={{ duration: 30, ease: "linear" }}
          />
        </div>
        <Button variant="outline" className="w-full mt-2" onClick={onComplete}>
          Done - Return to Scanner
        </Button>
      </div>
    </motion.div>
  );
}

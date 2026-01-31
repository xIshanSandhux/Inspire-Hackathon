"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { UserInfoResponse } from "@/api/useIdentity";

interface PersonInfoDisplayProps {
  userInfo: UserInfoResponse;
  onScanAnother: () => void;
}

// Helper to get display name and icon for document type
function getDocumentDisplay(docType: string): { name: string; icon: string } {
  const typeUpper = docType.toUpperCase();
  if (typeUpper.includes("PASSPORT")) {
    return { name: "Passport", icon: "🛂" };
  } else if (typeUpper.includes("BCID") || typeUpper.includes("BC_ID") || typeUpper.includes("BC ID")) {
    return { name: "BC ID", icon: "🪪" };
  } else if (typeUpper.includes("DRIVER") || typeUpper.includes("LICENSE")) {
    return { name: "Driver's License", icon: "🚗" };
  } else if (typeUpper.includes("HEALTH")) {
    return { name: "Health Card", icon: "🏥" };
  }
  // Default: format the type nicely
  return { 
    name: docType.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()), 
    icon: "📄" 
  };
}

export function PersonInfoDisplay({
  userInfo,
  onScanAnother,
}: PersonInfoDisplayProps) {
  const hasDocuments = userInfo.documents && Object.keys(userInfo.documents).length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 w-full max-w-lg"
    >
      {/* Success Header */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", delay: 0.2 }}
        className="flex justify-center"
      >
        <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-3xl"
          >
            ✓
          </motion.span>
        </div>
      </motion.div>

      <div className="text-center">
        <h2 className="text-xl font-semibold mb-1">Citizen Identified</h2>
        <p className="text-sm text-muted-foreground font-mono">
          ID: {userInfo.fingerprint_hash}
        </p>
      </div>

      {/* Meta Info */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Identity Record</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Status</span>
            <span className="text-green-600 font-medium">Verified</span>
          </div>
        </CardContent>
      </Card>

      {/* Documents */}
      {hasDocuments ? (
        <div className="space-y-4">
          {Object.entries(userInfo.documents).map(([docType, doc]) => {
            const display = getDocumentDisplay(docType);
            return (
              <Card key={docType}>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{display.icon} {display.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Document ID</span>
                    <span className="font-mono">{doc.id}</span>
                  </div>
                  {Object.entries(doc.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-muted-foreground">
                        {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                      </span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">No documents on file for this citizen.</p>
          </CardContent>
        </Card>
      )}

      {/* Action Button */}
      <Button onClick={onScanAnother} className="w-full" size="lg">
        Scan Another Citizen
      </Button>
    </motion.div>
  );
}

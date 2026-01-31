"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { ServiceSignOutButton } from "@/components/service-sign-out-button";
import { FingerprintScanner } from "@/components/fingerprint-scanner";
import { DocumentSelector } from "@/components/document-selector";
import { CameraCapture } from "@/components/camera-capture";
import { ExtractedInfoDisplay } from "@/components/extracted-info-display";
import {
  useUpsertIdentity,
  useUploadDocument,
  type Documents,
  type Document,
} from "@/api/useIdentity";

type FlowStep = "scan" | "select" | "capture" | "result";

export default function ServiceDashboard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<FlowStep>("scan");
  const [isScanning, setIsScanning] = useState(false);
  const [fingerprintId, setFingerprintId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Documents>({});
  const [selectedDocType, setSelectedDocType] = useState<"PASSPORT" | "BCID" | null>(null);
  const [extractedDocument, setExtractedDocument] = useState<Document | null>(null);

  const upsertIdentity = useUpsertIdentity();
  const uploadDocument = useUploadDocument();

  useEffect(() => {
    const serviceAuth = localStorage.getItem("service_auth");
    if (serviceAuth !== "authenticated") {
      router.push("/auth/service");
    }
  }, [router]);

  const handleScanComplete = async (id: string) => {
    setFingerprintId(id);
    setIsScanning(false);

    try {
      const result = await upsertIdentity.mutateAsync(id);
      setDocuments(result.documents || {});
      setCurrentStep("select");
    } catch (error) {
      console.error("Failed to upsert identity:", error);
      // For demo, continue anyway with empty documents
      setDocuments({});
      setCurrentStep("select");
    }
  };

  const handleDocumentSelect = (type: "PASSPORT" | "BCID") => {
    setSelectedDocType(type);
    setCurrentStep("capture");
  };

  const handleCapture = async (imageBase64: string) => {
    if (!fingerprintId || !selectedDocType) return;

    try {
      const result = await uploadDocument.mutateAsync({
        fingerprintId,
        documentType: selectedDocType,
        imageBase64,
      });

      const doc = result[selectedDocType];
      if (doc) {
        setExtractedDocument(doc);
        setCurrentStep("result");
      }
    } catch (error) {
      console.error("Failed to upload document:", error);
      // For demo, show mock result
      setExtractedDocument({
        id: selectedDocType === "PASSPORT" ? "P123456789" : "BC987654321",
        metadata:
          selectedDocType === "PASSPORT"
            ? { country: "Canada", expiry_date: "2030-12-31" }
            : { issued_by: "BC Services Card", issue_date: "2020-01-01" },
      });
      setCurrentStep("result");
    }
  };

  const handleCaptureCancel = () => {
    setSelectedDocType(null);
    setCurrentStep("select");
  };

  const handleReset = () => {
    setCurrentStep("scan");
    setFingerprintId(null);
    setDocuments({});
    setSelectedDocType(null);
    setExtractedDocument(null);
    setIsScanning(false);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4">
        <h1 className="text-xl font-bold">Identity Verification</h1>
        <ServiceSignOutButton />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <AnimatePresence mode="wait">
          {currentStep === "scan" && (
            <motion.div
              key="scan"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex flex-col items-center justify-center p-4"
            >
              <FingerprintScanner
                onScanComplete={handleScanComplete}
                isScanning={isScanning || upsertIdentity.isPending}
                setIsScanning={setIsScanning}
              />
              {upsertIdentity.isPending && (
                <p className="text-center text-sm text-muted-foreground mt-4">
                  Verifying identity...
                </p>
              )}
            </motion.div>
          )}

          {currentStep === "select" && (
            <motion.div
              key="select"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex items-center justify-center p-4"
            >
              <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                  <DocumentSelector
                    documents={documents}
                    onSelect={handleDocumentSelect}
                    onCancel={handleReset}
                  />
                </CardContent>
              </Card>
            </motion.div>
          )}

          {currentStep === "capture" && selectedDocType && (
            <motion.div
              key="capture"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex flex-col p-4"
              style={{ maxHeight: "calc(100vh - 80px)" }}
            >
              <CameraCapture
                documentType={selectedDocType}
                onCapture={handleCapture}
                onCancel={handleCaptureCancel}
                isUploading={uploadDocument.isPending}
              />
            </motion.div>
          )}

          {currentStep === "result" && extractedDocument && selectedDocType && (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex items-center justify-center p-4"
            >
              <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                  <ExtractedInfoDisplay
                    documentType={selectedDocType}
                    document={extractedDocument}
                    onComplete={handleReset}
                  />
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

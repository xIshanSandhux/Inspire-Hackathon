"use client";

import {
  DOCUMENT_TYPES,
  useCreateIdentity,
  useUploadDocument,
  type AddDocumentResponse,
  type Document,
  type Documents,
  type FrontendDocumentType,
} from "@/api/useIdentity";
import { CameraCapture } from "@/components/camera-capture";
import { DocumentSelector } from "@/components/document-selector";
import { ExtractedInfoDisplay } from "@/components/extracted-info-display";
import { FingerprintScanner } from "@/components/fingerprint-scanner";
import { ServiceSignOutButton } from "@/components/service-sign-out-button";
import { Card, CardContent } from "@/components/ui/card";
import { AnimatePresence, motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type FlowStep = "scan" | "select" | "capture" | "result";

// Helper function to convert base64 to File
function base64ToFile(base64: string, filename: string): File {
  const arr = base64.split(",");
  const mimeMatch = arr[0].match(/:(.*?);/);
  const mime = mimeMatch ? mimeMatch[1] : "image/jpeg";
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, { type: mime });
}

export default function ServiceDashboard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<FlowStep>("scan");
  const [isScanning, setIsScanning] = useState(false);
  const [fingerprintHash, setFingerprintHash] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Documents>({});
  const [selectedDocType, setSelectedDocType] =
    useState<FrontendDocumentType | null>(null);
  const [extractedDocument, setExtractedDocument] = useState<Document | null>(
    null,
  );
  const [extractedDocType, setExtractedDocType] = useState<string | null>(null);

  const createIdentity = useCreateIdentity();
  const uploadDocument = useUploadDocument();

  useEffect(() => {
    const serviceAuth = localStorage.getItem("service_auth");
    if (serviceAuth !== "authenticated") {
      router.push("/auth/service");
    }
  }, [router]);

  const handleScanComplete = async (id: string) => {
    setFingerprintHash(id);
    setIsScanning(false);

    try {
      await createIdentity.mutateAsync(id);
      // Identity created successfully, move to document selection
      setDocuments({});
      setCurrentStep("select");
    } catch (error) {
      console.error("Failed to create identity:", error);
      // For demo, continue anyway with empty documents
      setDocuments({});
      setCurrentStep("select");
    }
  };

  const handleDocumentSelect = (type: FrontendDocumentType) => {
    setSelectedDocType(type);
    setCurrentStep("capture");
  };

  const handleCapture = async (imageBase64: string) => {
    if (!fingerprintHash || !selectedDocType) return;

    try {
      // Convert base64 to File for multipart upload
      const imageFile = base64ToFile(imageBase64, `document_${Date.now()}.jpg`);

      // Pass document type for tailored extraction
      const result: AddDocumentResponse = await uploadDocument.mutateAsync({
        fingerprintHash,
        imageFile,
        documentType: selectedDocType,
      });

      // Extract document info from response
      setExtractedDocument({
        id: result.id,
        metadata: result.metadata,
      });
      setExtractedDocType(result.document_type);
      setCurrentStep("result");
    } catch (error) {
      console.error("Failed to upload document:", error);
      // For demo, show mock result with backend type
      const backendType = DOCUMENT_TYPES[selectedDocType];
      const mockData: Record<
        string,
        { id: string; metadata: Record<string, string> }
      > = {
        drivers_license: {
          id: "DL123456789",
          metadata: {
            issuing_authority: "British Columbia",
            expiry_date: "2030-12-31",
          },
        },
        passport: {
          id: "AB1234567",
          metadata: { country: "Canada", expiry_date: "2030-12-31" },
        },
        bc_services: {
          id: "9012345678",
          metadata: {
            issuing_authority: "BC Services",
            issue_date: "2020-01-01",
          },
        },
      };
      const mock = mockData[backendType] || mockData.drivers_license;
      setExtractedDocument({
        id: mock.id,
        metadata: mock.metadata,
      });
      setExtractedDocType(backendType);
      setCurrentStep("result");
    }
  };

  const handleCaptureCancel = () => {
    setSelectedDocType(null);
    setCurrentStep("select");
  };

  const handleReset = () => {
    setCurrentStep("scan");
    setFingerprintHash(null);
    setDocuments({});
    setSelectedDocType(null);
    setExtractedDocument(null);
    setExtractedDocType(null);
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
                isScanning={isScanning || createIdentity.isPending}
                setIsScanning={setIsScanning}
              />
              {createIdentity.isPending && (
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

          {currentStep === "result" &&
            extractedDocument &&
            extractedDocType && (
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
                      documentType={extractedDocType}
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

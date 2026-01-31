"use client";

import { motion } from "framer-motion";
import { DEMO_FINGERPRINT_ID } from "@/api/useIdentity";

interface FingerprintScannerProps {
  onScanComplete: (fingerprintId: string) => void;
  isScanning: boolean;
  setIsScanning: (scanning: boolean) => void;
}

export function FingerprintScanner({
  onScanComplete,
  isScanning,
  setIsScanning,
}: FingerprintScannerProps) {
  const handleScan = () => {
    if (isScanning) return;
    setIsScanning(true);

    // Simulate scanning delay
    setTimeout(() => {
      onScanComplete(DEMO_FINGERPRINT_ID);
    }, 2500);
  };

  return (
    <div className="flex flex-col items-center gap-12">
      <p className="text-muted-foreground text-center">
        {isScanning ? "Scanning fingerprint..." : "Tap to scan fingerprint"}
      </p>

      <motion.button
        onClick={handleScan}
        disabled={isScanning}
        className="relative w-40 h-40 rounded-full bg-muted flex items-center justify-center cursor-pointer disabled:cursor-not-allowed"
        whileHover={!isScanning ? { scale: 1.05 } : {}}
        whileTap={!isScanning ? { scale: 0.95 } : {}}
      >
        {/* Fingerprint Icon */}
        <svg
          className="w-20 h-20 text-muted-foreground"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4" />
          <path d="M14 13.12c0 2.38 0 6.38-1 8.88" />
          <path d="M17.29 21.02c.12-.6.43-2.3.5-3.02" />
          <path d="M2 12a10 10 0 0 1 18-6" />
          <path d="M2 16h.01" />
          <path d="M21.8 16c.2-2 .131-5.354 0-6" />
          <path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2" />
          <path d="M8.65 22c.21-.66.45-1.32.57-2" />
          <path d="M9 6.8a6 6 0 0 1 9 5.2v2" />
        </svg>


        {/* Scanning animation rings */}
        {isScanning && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary"
              initial={{ scale: 1, opacity: 0.8 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary"
              initial={{ scale: 1, opacity: 0.8 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.3 }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary"
              initial={{ scale: 1, opacity: 0.8 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.6 }}
            />
          </>
        )}

        {/* Progress overlay */}
        {isScanning && (
          <motion.div
            className="absolute inset-0 rounded-full bg-primary/20"
            initial={{ clipPath: "inset(100% 0 0 0)" }}
            animate={{ clipPath: "inset(0% 0 0 0)" }}
            transition={{ duration: 3, ease: "linear" }}
          />
        )}
      </motion.button>

      {isScanning && (
        <motion.p
          className="text-sm text-primary"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          Please hold still...
        </motion.p>
      )}
    </div>
  );
}

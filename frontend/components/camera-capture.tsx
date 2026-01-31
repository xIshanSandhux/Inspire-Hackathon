"use client";

import { useRef, useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface CameraCaptureProps {
  documentType: "PASSPORT" | "BCID";
  onCapture: (imageBase64: string) => void;
  onCancel: () => void;
  isUploading: boolean;
}

export function CameraCapture({
  documentType,
  onCapture,
  onCancel,
  isUploading,
}: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const initCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: 1280, height: 720 },
        });
        if (!mounted) {
          mediaStream.getTracks().forEach((track) => track.stop());
          return;
        }
        streamRef.current = mediaStream;
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        setError(null);
      } catch (err) {
        if (mounted) {
          setError("Unable to access camera. Please grant camera permissions.");
        }
        console.error("Camera error:", err);
      }
    };

    initCamera();

    return () => {
      mounted = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: 1280, height: 720 },
      });
      streamRef.current = mediaStream;
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setError(null);
    } catch (err) {
      setError("Unable to access camera. Please grant camera permissions.");
      console.error("Camera error:", err);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL("image/jpeg", 0.8);
        setCapturedImage(imageData);
        stopCamera();
      }
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  const confirmPhoto = () => {
    if (capturedImage) {
      onCapture(capturedImage);
    }
  };

  const handleCancel = () => {
    stopCamera();
    onCancel();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col h-full"
    >
      {/* Camera View - Takes most of the space with fixed aspect ratio */}
      <div className="flex-1 relative bg-black rounded-2xl overflow-hidden mx-auto w-full max-w-lg aspect-[16/9]">
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center text-white text-center p-6">
            <div>
              <div className="text-4xl mb-4">📷</div>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        ) : capturedImage ? (
          <img
            src={capturedImage}
            alt="Captured document"
            className="w-full h-full object-contain"
          />
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            {/* Corner guides */}
            <div className="absolute inset-3 pointer-events-none">
              {/* Top Left */}
              <div className="absolute top-0 left-0 w-8 h-8 border-t-3 border-l-3 border-white rounded-tl-lg" />
              {/* Top Right */}
              <div className="absolute top-0 right-0 w-8 h-8 border-t-3 border-r-3 border-white rounded-tr-lg" />
              {/* Bottom Left */}
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-3 border-l-3 border-white rounded-bl-lg" />
              {/* Bottom Right */}
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-3 border-r-3 border-white rounded-br-lg" />
            </div>
            {/* Scanning line animation */}
            <motion.div
              className="absolute left-6 right-6 h-0.5 bg-primary/80"
              initial={{ top: "10%" }}
              animate={{ top: ["10%", "90%", "10%"] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
          </>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />

      {/* Bottom Section */}
      <div className="pt-6 space-y-4">
        {/* Instructions */}
        <div className="text-center">
          <p className="text-lg font-medium">
            {documentType === "PASSPORT" ? "Passport" : "BC ID"}
          </p>
          <p className="text-sm text-muted-foreground">
            {capturedImage
              ? "Does this look good?"
              : "Align your document within the frame"}
          </p>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 max-w-sm mx-auto w-full">
          {capturedImage ? (
            <>
              <Button
                variant="outline"
                size="lg"
                className="flex-1"
                onClick={retakePhoto}
                disabled={isUploading}
              >
                Retake
              </Button>
              <Button
                size="lg"
                className="flex-1"
                onClick={confirmPhoto}
                disabled={isUploading}
              >
                {isUploading ? "Processing..." : "Confirm"}
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                size="lg"
                className="flex-1"
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button
                size="lg"
                className="flex-1"
                onClick={capturePhoto}
                disabled={!!error}
              >
                📸 Capture
              </Button>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}

"use client";

import type { Documents, FrontendDocumentType } from "@/api/useIdentity";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

interface DocumentSelectorProps {
  documents: Documents;
  onSelect: (type: FrontendDocumentType) => void;
  onCancel: () => void;
}

export function DocumentSelector({
  documents,
  onSelect,
  onCancel,
}: DocumentSelectorProps) {
  // Check for existing documents by backend type
  const hasPassport = !!documents.passport || !!documents.PASSPORT;
  const hasBCServices =
    !!documents.bc_services || !!documents.BC_SERVICES;
  const hasBCID = !!documents.bcid || !!documents.BCID;
  const hasDriversLicense =
    !!documents.drivers_license || !!documents.DRIVERS_LICENSE;
  const isNewUser =
    !hasPassport && !hasBCServices && !hasBCID && !hasDriversLicense;

  // Get document by checking multiple possible keys
  const getDocument = (keys: string[]) => {
    for (const key of keys) {
      if (documents[key]) return documents[key];
    }
    return null;
  };

  const passportDoc = getDocument(["passport", "PASSPORT"]);
  const bcServicesDoc = getDocument(["bc_services", "BC_SERVICES"]);
  const bcidDoc = getDocument(["bcid", "BCID"]);
  const driversLicenseDoc = getDocument(["drivers_license", "DRIVERS_LICENSE"]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">
          {isNewUser ? "Welcome, New User!" : "Welcome Back!"}
        </h2>
        <p className="text-muted-foreground">
          {isNewUser
            ? "Please add a document to verify your identity"
            : "Select a document to add or update"}
        </p>
      </div>

      {/* Existing documents display */}
      {!isNewUser && (
        <div className="space-y-3">
          <p className="text-sm font-medium">Your Documents:</p>
          <div className="grid gap-3">
            {driversLicenseDoc && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> Driver&apos;s
                    License
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>ID: {driversLicenseDoc.id}</p>
                  {driversLicenseDoc.metadata.issuing_authority && (
                    <p>
                      Issued by:{" "}
                      {String(driversLicenseDoc.metadata.issuing_authority)}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
            {passportDoc && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> Passport
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>ID: {passportDoc.id}</p>
                  {passportDoc.metadata.country && (
                    <p>Country: {String(passportDoc.metadata.country)}</p>
                  )}
                </CardContent>
              </Card>
            )}
            {bcServicesDoc && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> BC Services Card
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>PHN: {bcServicesDoc.id}</p>
                  {bcServicesDoc.metadata.issuing_authority && (
                    <p>
                      Issued by:{" "}
                      {String(bcServicesDoc.metadata.issuing_authority)}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
            {bcidDoc && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> BC ID Card
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>BCID: {bcidDoc.id}</p>
                  {bcidDoc.metadata.issuing_authority && (
                    <p>
                      Issued by:{" "}
                      {String(bcidDoc.metadata.issuing_authority)}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Add document options */}
      <div className="space-y-3">
        <p className="text-sm font-medium">Add a Document:</p>
        <div className="grid gap-3">
          <Button
            variant="outline"
            className="h-16 justify-start gap-3"
            onClick={() => onSelect("DRIVERS_LICENSE")}
            disabled={hasDriversLicense}
          >
            <span className="text-2xl">🚗</span>
            <div className="text-left">
              <p className="font-medium">Driver&apos;s License</p>
              <p className="text-xs text-muted-foreground">
                {hasDriversLicense
                  ? "Already added"
                  : "Add your driver's license"}
              </p>
            </div>
          </Button>
          <Button
            variant="outline"
            className="h-16 justify-start gap-3"
            onClick={() => onSelect("PASSPORT")}
            disabled={hasPassport}
          >
            <span className="text-2xl">🛂</span>
            <div className="text-left">
              <p className="font-medium">Passport</p>
              <p className="text-xs text-muted-foreground">
                {hasPassport ? "Already added" : "Add your passport"}
              </p>
            </div>
          </Button>
          <Button
            variant="outline"
            className="h-16 justify-start gap-3"
            onClick={() => onSelect("BC_SERVICES")}
            disabled={hasBCServices}
          >
            <span className="text-2xl">🪪</span>
            <div className="text-left">
              <p className="font-medium">BC Services Card</p>
              <p className="text-xs text-muted-foreground">
                {hasBCServices
                  ? "Already added"
                  : "Add your BC Services Card (PHN)"}
              </p>
            </div>
          </Button>
          <Button
            variant="outline"
            className="h-16 justify-start gap-3"
            onClick={() => onSelect("BCID")}
            disabled={hasBCID}
          >
            <span className="text-2xl">🪪</span>
            <div className="text-left">
              <p className="font-medium">BC ID Card</p>
              <p className="text-xs text-muted-foreground">
                {hasBCID ? "Already added" : "Add your BC ID Card (BCID)"}
              </p>
            </div>
          </Button>
        </div>
      </div>

      {/* Show done if all documents added */}
      {hasPassport && hasBCServices && hasBCID && hasDriversLicense && (
        <p className="text-center text-sm text-muted-foreground">
          All documents have been added!
        </p>
      )}

      <Button variant="ghost" className="w-full" onClick={onCancel}>
        Cancel & Start Over
      </Button>
    </motion.div>
  );
}

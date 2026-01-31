"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Documents } from "@/api/useIdentity";

interface DocumentSelectorProps {
  documents: Documents;
  onSelect: (type: "PASSPORT" | "BCID") => void;
  onCancel: () => void;
}

export function DocumentSelector({
  documents,
  onSelect,
  onCancel,
}: DocumentSelectorProps) {
  const hasPassport = !!documents.PASSPORT;
  const hasBCID = !!documents.BCID;
  const isNewUser = !hasPassport && !hasBCID;

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
            : "Select a document to add (you cannot update existing documents)"}
        </p>
      </div>

      {/* Existing documents display */}
      {!isNewUser && (
        <div className="space-y-3">
          <p className="text-sm font-medium">Your Documents:</p>
          <div className="grid gap-3">
            {hasPassport && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> Passport
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>ID: {documents.PASSPORT?.id}</p>
                  <p>Country: {documents.PASSPORT?.metadata.country}</p>
                </CardContent>
              </Card>
            )}
            {hasBCID && (
              <Card className="bg-muted/50">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <span className="text-green-500">✓</span> BC ID
                  </CardTitle>
                </CardHeader>
                <CardContent className="py-2 text-xs text-muted-foreground">
                  <p>ID: {documents.BCID?.id}</p>
                  <p>Issued by: {documents.BCID?.metadata.issued_by}</p>
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
            onClick={() => onSelect("BCID")}
            disabled={hasBCID}
          >
            <span className="text-2xl">🪪</span>
            <div className="text-left">
              <p className="font-medium">BC ID</p>
              <p className="text-xs text-muted-foreground">
                {hasBCID ? "Already added" : "Add your BC Services Card"}
              </p>
            </div>
          </Button>
        </div>
      </div>

      {/* Show done if all documents added */}
      {hasPassport && hasBCID && (
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

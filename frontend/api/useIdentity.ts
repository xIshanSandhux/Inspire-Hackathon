import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Set to true to use mock responses, false to use real API
const USE_MOCK = true;

// Fixed fingerprint ID for demo purposes
export const DEMO_FINGERPRINT_ID = "fp_demo_123456789";

interface DocumentMetadata {
  [key: string]: string;
}

interface Document {
  id: string;
  metadata: DocumentMetadata;
}

interface Documents {
  PASSPORT?: Document;
  BCID?: Document;
}

interface UpsertIdentityResponse {
  fingerprint_id: string;
  documents: Documents;
}

interface UploadDocumentResponse {
  PASSPORT?: Document;
  BCID?: Document;
}

// Get M2M token from localStorage
const getM2MToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("service_token") || "";
  }
  return "";
};

// Mock data storage (persists during session)
let mockDocuments: Documents = {};

// Mock delay helper
const mockDelay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Upsert Identity - sends fingerprint ID and verifies with M2M token
export const useUpsertIdentity = () => {
  return useMutation({
    mutationFn: async (fingerprintId: string): Promise<UpsertIdentityResponse> => {
      if (USE_MOCK) {
        await mockDelay(1000);
        return {
          fingerprint_id: fingerprintId,
          documents: mockDocuments,
        };
      }

      const response = await fetch(`${API_BASE_URL}/upsert-identity`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getM2MToken()}`,
        },
        body: JSON.stringify({ fingerprint_id: fingerprintId }),
      });

      if (!response.ok) {
        throw new Error("Failed to upsert identity");
      }

      return response.json();
    },
  });
};

// Upload Document - sends document image with type
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: async ({
      fingerprintId,
      documentType,
      imageBase64,
    }: {
      fingerprintId: string;
      documentType: "PASSPORT" | "BCID";
      imageBase64: string;
    }): Promise<UploadDocumentResponse> => {
      if (USE_MOCK) {
        await mockDelay(2000); // Simulate processing time
        
        const mockDoc: Document =
          documentType === "PASSPORT"
            ? {
                id: "P" + Math.random().toString(36).substring(2, 11).toUpperCase(),
                metadata: {
                  country: "Canada",
                  expiry_date: "2030-12-31",
                  first_name: "John",
                  last_name: "Doe",
                },
              }
            : {
                id: "BC" + Math.random().toString(36).substring(2, 11).toUpperCase(),
                metadata: {
                  issued_by: "BC Services Card",
                  issue_date: "2020-01-01",
                  first_name: "John",
                  last_name: "Doe",
                },
              };

        // Store in mock storage
        mockDocuments[documentType] = mockDoc;

        return { [documentType]: mockDoc };
      }

      const response = await fetch(`${API_BASE_URL}/upload-document`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getM2MToken()}`,
        },
        body: JSON.stringify({
          fingerprint_id: fingerprintId,
          document_type: documentType,
          image: imageBase64,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to upload document");
      }

      return response.json();
    },
  });
};

// Get User Info by fingerprint ID
interface UserInfoResponse {
  fingerprint_id: string;
  documents: Documents;
  created_at?: string;
  last_verified?: string;
}

export const useUserInfo = () => {
  return useMutation({
    mutationFn: async (fingerprintId: string): Promise<UserInfoResponse> => {
      if (USE_MOCK) {
        await mockDelay(1500);
        
        // Return mock user data
        return {
          fingerprint_id: fingerprintId,
          documents: mockDocuments,
          created_at: "2024-06-15T10:30:00Z",
          last_verified: new Date().toISOString(),
        };
      }

      const response = await fetch(`${API_BASE_URL}/id`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getM2MToken()}`,
        },
        body: JSON.stringify({ fingerprint_id: fingerprintId }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user info");
      }

      return response.json();
    },
  });
};

// Reset mock data (useful for testing)
export const resetMockData = () => {
  mockDocuments = {};
};

export type { Documents, Document, UpsertIdentityResponse, UploadDocumentResponse, UserInfoResponse };

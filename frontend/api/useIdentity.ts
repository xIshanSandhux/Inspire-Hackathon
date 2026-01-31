import { useMutation } from "@tanstack/react-query";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Set to true to use mock responses, false to use real API
const USE_MOCK = false;

// Fixed fingerprint ID for demo purposes
export const DEMO_FINGERPRINT_ID = "fp_demo_123456789";

interface DocumentMetadata {
  [key: string]: unknown;
}

interface Document {
  id: string;
  metadata: DocumentMetadata;
}

// Documents keyed by document_type (e.g., "PASSPORT", "BCID", etc.)
interface Documents {
  [documentType: string]: Document;
}

// Response from /identity/create
interface CreateIdentityResponse {
  fingerprint_hash: string;
}

// Response from /identity/retrieve
interface RetrieveIdentityResponse {
  fingerprint_hash: string;
  documents: Documents;
}

// Response from /document/add-document
interface AddDocumentResponse {
  fingerprint_hash: string;
  document_type: string;
  id: string;
  metadata: DocumentMetadata;
  confidence: number;
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

// Create Identity - sends fingerprint hash and creates identity if not exists
export const useCreateIdentity = () => {
  return useMutation({
    mutationFn: async (fingerprintHash: string): Promise<CreateIdentityResponse> => {
      if (USE_MOCK) {
        await mockDelay(1000);
        return {
          fingerprint_hash: fingerprintHash,
        };
      }

      const response = await fetch(`${API_BASE_URL}/identity/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getM2MToken()}`,
        },
        body: JSON.stringify({ fingerprint_hash: fingerprintHash }),
      });

      if (!response.ok) {
        throw new Error("Failed to create identity");
      }

      return response.json();
    },
  });
};

// Legacy alias for backwards compatibility
export const useUpsertIdentity = useCreateIdentity;

// Upload Document - sends document image via multipart form data
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: async ({
      fingerprintHash,
      imageFile,
    }: {
      fingerprintHash: string;
      imageFile: File;
    }): Promise<AddDocumentResponse> => {
      if (USE_MOCK) {
        await mockDelay(2000); // Simulate processing time
        
        const mockDoc: Document = {
          id: "DOC" + Math.random().toString(36).substring(2, 11).toUpperCase(),
          metadata: {
            country: "Canada",
            expiry_date: "2030-12-31",
            first_name: "John",
            last_name: "Doe",
          },
        };

        // Store in mock storage with a generic type
        const mockDocType = "PASSPORT";
        mockDocuments[mockDocType] = mockDoc;

        return {
          fingerprint_hash: fingerprintHash,
          document_type: mockDocType,
          id: mockDoc.id,
          metadata: mockDoc.metadata,
          confidence: 0.95,
        };
      }

      // Use FormData for multipart/form-data upload
      const formData = new FormData();
      formData.append("fingerprint_hash", fingerprintHash);
      formData.append("image", imageFile);

      const response = await fetch(`${API_BASE_URL}/document/add-document`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${getM2MToken()}`,
          // Note: Don't set Content-Type for FormData, browser sets it with boundary
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to upload document");
      }

      return response.json();
    },
  });
};

// Get User Info by fingerprint hash (retrieves identity with all documents)
interface UserInfoResponse {
  fingerprint_hash: string;
  documents: Documents;
}

export const useUserInfo = () => {
  return useMutation({
    mutationFn: async (fingerprintHash: string): Promise<UserInfoResponse> => {
      if (USE_MOCK) {
        await mockDelay(1500);
        
        // Return mock user data
        return {
          fingerprint_hash: fingerprintHash,
          documents: mockDocuments,
        };
      }

      const response = await fetch(`${API_BASE_URL}/identity/retrieve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getM2MToken()}`,
        },
        body: JSON.stringify({ fingerprint_hash: fingerprintHash }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch user info");
      }

      return response.json();
    },
  });
};

// Retrieve Identity - alias for useUserInfo for clearer naming
export const useRetrieveIdentity = useUserInfo;

// Reset mock data (useful for testing)
export const resetMockData = () => {
  mockDocuments = {};
};

export type { 
  Documents, 
  Document, 
  CreateIdentityResponse, 
  RetrieveIdentityResponse,
  AddDocumentResponse, 
  UserInfoResponse 
};

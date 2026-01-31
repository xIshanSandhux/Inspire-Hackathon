import { useMutation } from "@tanstack/react-query";
import { apiUrl, getHeaders, getHeadersWithClerkToken } from "./config";

// Set to true to use mock responses, false to use real API
const USE_MOCK = false;

// Fixed fingerprint ID for demo purposes
export const DEMO_FINGERPRINT_ID = "fp_demo_123456789";

// Document type mapping: Frontend display name -> Backend API value
export const DOCUMENT_TYPES = {
  DRIVERS_LICENSE: "drivers_license",
  BC_SERVICES: "bc_services",
  BCID: "bcid", // BC ID Card (ID format: BCID: <string>)
  PASSPORT: "passport",
} as const;

export type FrontendDocumentType = keyof typeof DOCUMENT_TYPES;
export type BackendDocumentType = (typeof DOCUMENT_TYPES)[FrontendDocumentType];

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

// Mock data storage (persists during session)
let mockDocuments: Documents = {};

// Mock delay helper
const mockDelay = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Create Identity - sends fingerprint hash and creates identity if not exists
export const useCreateIdentity = () => {
  return useMutation({
    mutationFn: async (
      fingerprintHash: string,
    ): Promise<CreateIdentityResponse> => {
      if (USE_MOCK) {
        await mockDelay(1000);
        return {
          fingerprint_hash: fingerprintHash,
        };
      }

      const response = await fetch(apiUrl("/identity/create"), {
        method: "POST",
        headers: getHeaders("application/json"),
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
      documentType,
    }: {
      fingerprintHash: string;
      imageFile: File;
      documentType?: FrontendDocumentType;
    }): Promise<AddDocumentResponse> => {
      // Map frontend type to backend type
      const backendDocType = documentType
        ? DOCUMENT_TYPES[documentType]
        : undefined;

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

        // Store in mock storage with the document type
        const mockDocType = backendDocType || "passport";
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

      // Add document_type if provided (enables tailored extraction prompts)
      if (backendDocType) {
        formData.append("document_type", backendDocType);
      }

      const response = await fetch(apiUrl("/document/add-document"), {
        method: "POST",
        headers: getHeaders(),
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
    mutationFn: async ({
      fingerprintHash,
      clerkToken,
    }: {
      fingerprintHash: string;
      clerkToken?: string;
    }): Promise<UserInfoResponse> => {
      if (USE_MOCK) {
        await mockDelay(1500);

        // Return mock user data
        return {
          fingerprint_hash: fingerprintHash,
          documents: mockDocuments,
        };
      }

      // Use Clerk token if provided, otherwise fall back to default headers (M2M token)
      const headers = clerkToken
        ? getHeadersWithClerkToken(clerkToken, "application/json")
        : getHeaders("application/json");

      const response = await fetch(apiUrl("/identity/retrieve"), {
        method: "POST",
        headers,
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
  AddDocumentResponse,
  CreateIdentityResponse,
  Document,
  Documents,
  RetrieveIdentityResponse,
  UserInfoResponse,
};

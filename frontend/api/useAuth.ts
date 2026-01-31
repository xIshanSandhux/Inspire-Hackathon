import { useMutation } from "@tanstack/react-query";

// ============ Create User ============

interface CreateUserParams {
  email: string;
  password: string;
  role: "gov" | "admin";
  firstName?: string;
  lastName?: string;
}

interface CreateUserResponse {
  success: boolean;
  user: {
    id: string;
    email: string;
    role: string;
    firstName: string | null;
    lastName: string | null;
  };
}

export const useCreateUser = () => {
  return useMutation({
    mutationFn: async (params: CreateUserParams): Promise<CreateUserResponse> => {
      const response = await fetch("/api/create-user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to create user");
      }

      return data;
    },
  });
};

// ============ Create M2M Token ============

interface CreateM2MTokenResponse {
  success: boolean;
  token: string;
  expiresAt: string;
  validityDays: number;
}

export const useCreateM2MToken = () => {
  return useMutation({
    mutationFn: async (): Promise<CreateM2MTokenResponse> => {
      const response = await fetch("/api/create-m2m-token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to create M2M token");
      }

      return data;
    },
  });
};

export type { CreateUserParams, CreateUserResponse, CreateM2MTokenResponse };

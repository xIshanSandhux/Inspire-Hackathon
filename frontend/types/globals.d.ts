export {};

declare global {
  interface CustomJwtSessionClaims {
    metadata?: {
      role?: "gov" | "admin" | "service";
    };
    publicMetadata?: {
      role?: "gov" | "admin" | "service";
    };
  }
}

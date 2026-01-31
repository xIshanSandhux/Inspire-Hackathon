export {};

declare global {
  interface CustomJwtSessionClaims {
    metadata: {
      role?: "gov" | "admin" | "service";
    };
  }
}

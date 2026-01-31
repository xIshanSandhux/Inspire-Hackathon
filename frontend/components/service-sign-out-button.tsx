"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export function ServiceSignOutButton() {
  const router = useRouter();

  const handleSignOut = () => {
    localStorage.removeItem("service_auth");
    localStorage.removeItem("service_token");
    router.push("/auth/service");
  };

  return (
    <Button variant="outline" onClick={handleSignOut}>
      Sign Out
    </Button>
  );
}

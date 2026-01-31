import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm space-y-6">
        <h1 className="text-2xl font-bold text-center">Select Portal</h1>
        <div className="space-y-3">
          <Link
            href="/auth/service"
            className="flex items-center justify-center w-full h-12 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            Service Login
          </Link>
          <Link
            href="/auth/gov"
            className="flex items-center justify-center w-full h-12 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            Government Login
          </Link>
          <Link
            href="/auth/admin"
            className="flex items-center justify-center w-full h-12 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            Admin Login
          </Link>
        </div>
      </div>
    </div>
  );
}

"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import { ReactNode } from "react";

// Get Convex URL from environment variables with fallback for development
const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL || "";

// Only create ConvexReactClient if URL is provided
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null;

export function ConvexClientProvider({ children }: { children: ReactNode }) {
  // If no Convex URL is configured, render children without Convex provider
  if (!convex) {
    console.warn(
      "NEXT_PUBLIC_CONVEX_URL is not set. Convex features will be unavailable.",
    );
    return <>{children}</>;
  }

  return <ConvexProvider client={convex}>{children}</ConvexProvider>;
}
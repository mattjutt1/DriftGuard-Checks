import type { Metadata, Viewport } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ConvexClientProvider } from "./ConvexClientProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#3b82f6",
};

export const metadata: Metadata = {
  title: "PromptEvolver - Advanced AI Prompt Optimization",
  description:
    "Transform your prompts with Microsoft PromptWizard methodology powered by Qwen3-4B. Get systematic improvements in clarity, specificity, and engagement through AI-driven optimization.",
  keywords: [
    "AI prompt optimization",
    "Microsoft PromptWizard",
    "Qwen3",
    "prompt engineering",
    "AI assistant",
    "prompt enhancement",
    "machine learning",
    "natural language processing",
  ],
  authors: [{ name: "PromptEvolver Team" }],
  creator: "PromptEvolver",
  publisher: "PromptEvolver",
  openGraph: {
    type: "website",
    locale: "en_US",
    title: "PromptEvolver - Advanced AI Prompt Optimization",
    description:
      "Transform your prompts with Microsoft PromptWizard methodology powered by Qwen3-4B",
    siteName: "PromptEvolver",
  },
  twitter: {
    card: "summary_large_image",
    title: "PromptEvolver - Advanced AI Prompt Optimization",
    description:
      "Transform your prompts with Microsoft PromptWizard methodology powered by Qwen3-4B",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body
        className={`${inter.variable} ${geistMono.variable} antialiased font-sans text-gray-900 bg-gray-50`}
      >
        <ConvexClientProvider>{children}</ConvexClientProvider>
      </body>
    </html>
  );
}

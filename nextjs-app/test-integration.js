#!/usr/bin/env node

/**
 * Quick Integration Test Script
 * Tests basic Convex connectivity and function availability
 */

const { ConvexHttpClient } = require("convex/browser");

async function testIntegration() {
  console.log("🧪 Testing PromptEvolver Integration");
  console.log("=====================================");

  // Check environment
  const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
  if (!convexUrl) {
    console.error("❌ NEXT_PUBLIC_CONVEX_URL not set in .env.local");
    console.log("💡 Run 'npx convex dev' and copy the URL to .env.local");
    process.exit(1);
  }

  console.log("✅ Convex URL found:", convexUrl);

  try {
    // Test basic connection
    const client = new ConvexHttpClient(convexUrl);
    console.log("✅ Convex client created");

    // Test health check
    console.log("🔍 Testing health check...");
    const health = await client.action("actions.checkOllamaHealth", {});
    console.log("✅ Health check result:", health);

    // Test demo data seeding
    console.log("🌱 Seeding demo data...");
    const seedResult = await client.mutation("seedData.seedDemoData", {});
    console.log("✅ Demo data seeded:", seedResult);

    // Test session retrieval
    console.log("📊 Testing session retrieval...");
    const sessions = await client.query("sessions.getRecentSessions", { limit: 3 });
    console.log("✅ Retrieved sessions:", sessions.length);

    console.log("\n🎉 All integration tests passed!");
    console.log("🚀 Your advanced UI should work perfectly!");

  } catch (error) {
    console.error("❌ Integration test failed:", error.message);
    console.log("\n🔧 Troubleshooting steps:");
    console.log("1. Ensure 'npx convex dev' is running");
    console.log("2. Check your .env.local file has the correct URL");
    console.log("3. Verify all Convex functions are deployed");
    process.exit(1);
  }
}

testIntegration();
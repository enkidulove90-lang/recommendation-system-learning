import path from "node:path";
import { fileURLToPath } from "node:url";

import { cloudflareTest, readD1Migrations } from "@cloudflare/vitest-plugin";
import { defineConfig } from "vitest/config";

const root = path.dirname(fileURLToPath(import.meta.url));
process.env.WRANGLER_LOG_PATH = path.join(root, ".wrangler", "logs", "wrangler.log");

export default defineConfig({
  plugins: [
    cloudflareTest(async () => ({
      wrangler: { configPath: path.join(root, "wrangler.test.jsonc") },
      miniflare: {
        bindings: {
          ARTIFACT_STORAGE_ENABLED: "true",
          BROWSER_AUTH_ENABLED: "true",
          GITHUB_OAUTH_CLIENT_ID: "test-github-client-id",
          GITHUB_OAUTH_CLIENT_SECRET: "test-github-client-secret",
          GITHUB_OWNER_IDS: "123456",
          OWNER_IDENTITIES: "owner@example.com,github:123456",
          GITHUB_TOKEN: "test-github-token",
          PUBLIC_BASE_URL: "https://paper-intake.example",
          PUBLISH_CALLBACK_TOKEN: "test-callback-token",
          SESSION_SIGNING_KEY: "test-signing-key-with-at-least-32-bytes",
          WORKER_TOKEN: "test-worker-token",
          TEST_MIGRATIONS: await readD1Migrations(path.join(root, "migrations")),
        },
      },
    })),
  ],
  test: {
    setupFiles: ["./test/apply-migrations.ts"],
  },
});

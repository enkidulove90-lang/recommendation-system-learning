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
          ACCESS_IDENTITY_HEADER: "cf-access-authenticated-user-email",
          ARTIFACT_STORAGE_ENABLED: "true",
          OWNER_IDENTITIES: "owner@example.com",
          GITHUB_TOKEN: "test-github-token",
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

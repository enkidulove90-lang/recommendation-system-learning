import { spawnSync } from "node:child_process";
import path from "node:path";

const result = spawnSync(
  process.execPath,
  [
    path.join("node_modules", "wrangler", "bin", "wrangler.js"),
    "types",
    "src/worker-configuration.d.ts",
  ],
  {
    env: {
      ...process.env,
      WRANGLER_LOG_PATH: path.resolve(".wrangler", "logs", "wrangler.log"),
    },
    stdio: "inherit",
  },
);

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);

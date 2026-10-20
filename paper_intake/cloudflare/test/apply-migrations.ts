import { env } from "cloudflare:workers";
import { applyD1Migrations } from "cloudflare:test";
import { beforeEach } from "vitest";

type MigrationList = Parameters<typeof applyD1Migrations>[1];
const testEnv = env as Env & {
  TEST_MIGRATIONS: MigrationList;
  ARTIFACTS: R2Bucket;
};

beforeEach(async () => {
  await applyD1Migrations(testEnv.DB, testEnv.TEST_MIGRATIONS);
  await testEnv.DB.batch([
    testEnv.DB.prepare("DELETE FROM job_events"),
    testEnv.DB.prepare("DELETE FROM publications"),
    testEnv.DB.prepare("DELETE FROM artifacts"),
    testEnv.DB.prepare("DELETE FROM jobs"),
    testEnv.DB.prepare("DELETE FROM papers"),
    testEnv.DB.prepare("DELETE FROM login_codes"),
    testEnv.DB.prepare("DELETE FROM oauth_states"),
  ]);
  const objects = await testEnv.ARTIFACTS.list();
  if (objects.objects.length > 0) {
    await testEnv.ARTIFACTS.delete(objects.objects.map((object) => object.key));
  }
});

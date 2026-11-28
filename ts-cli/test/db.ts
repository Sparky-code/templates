// Test helper: a fresh SQLite database with every migration in
// prisma/migrations applied, so tests always run against the real schema.
import { mkdtempSync, readdirSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { type Db, openDb } from '../src/db.ts';

const migrations = fileURLToPath(new URL('../prisma/migrations/', import.meta.url));

export async function testDb(): Promise<{ db: Db; dir: string }> {
  const dir = mkdtempSync(join(tmpdir(), 'test-db-'));
  const db = openDb(`file:${join(dir, 'test.db')}`);
  const folders = readdirSync(migrations, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort();
  for (const folder of folders) {
    const sql = readFileSync(join(migrations, folder, 'migration.sql'), 'utf8');
    for (const statement of sql.split(/;\s*$/m)) {
      const body = statement.replace(/^--.*$/gm, '').trim();
      if (body) await db.$executeRawUnsafe(body);
    }
  }
  return { db, dir };
}

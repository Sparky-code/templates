// The job runner: every scheduled job goes through runJob, which
//  - holds a lock file so two runs can't overlap,
//  - records the run (start, end, outcome) in the database,
//  - sends a push notification (ntfy) when a run fails,
//  - sets a non-zero exit code on failure.
import { closeSync, openSync, readFileSync, rmSync, writeSync } from 'node:fs';
import type { Db } from './db.ts';

export interface JobContext {
  dryRun: boolean;
  /** Most items the job may post or send in this run. */
  max: number;
  log: (message: string) => void;
}

export interface RunOptions {
  db: Db;
  lockPath: string;
  dryRun: boolean;
  max: number;
  notify?: (message: string) => Promise<void>;
  log?: (message: string) => void;
}

export class LockedError extends Error {}

export function acquireLock(path: string): () => void {
  let fd: number;
  try {
    fd = openSync(path, 'wx');
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code !== 'EEXIST') throw err;
    const pid = Number(readFileSync(path, 'utf8'));
    if (pid && isAlive(pid)) throw new LockedError(`another run (pid ${pid}) holds ${path}`);
    rmSync(path, { force: true }); // stale lock from a crashed run
    fd = openSync(path, 'wx');
  }
  writeSync(fd, String(process.pid));
  closeSync(fd);
  return () => rmSync(path, { force: true });
}

function isAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

/** Runs `fn` as job `name`. Returns true on success. */
export async function runJob(
  name: string,
  fn: (ctx: JobContext) => Promise<string | undefined>,
  { db, lockPath, dryRun, max, notify, log = console.log }: RunOptions,
): Promise<boolean> {
  const release = acquireLock(lockPath);
  const run = await db.run.create({ data: { job: name, dryRun } });
  try {
    const detail = await fn({ dryRun, max, log });
    await db.run.update({
      where: { id: run.id },
      data: { finishedAt: new Date(), ok: true, detail: detail ?? null },
    });
    return true;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await db.run.update({
      where: { id: run.id },
      data: { finishedAt: new Date(), ok: false, detail: message },
    });
    log(`${name} failed: ${message}`);
    await notify?.(`${name} failed: ${message}`).catch(() => {});
    process.exitCode = 1;
    return false;
  } finally {
    release();
  }
}

/** Push notification via ntfy (https://ntfy.sh) if NTFY_URL is set. */
export function ntfyNotifier(
  url = process.env.NTFY_URL,
  fetchFn: typeof fetch = fetch,
): ((message: string) => Promise<void>) | undefined {
  if (!url) return undefined;
  return async (message) => {
    await fetchFn(url, { method: 'POST', body: message, headers: { Title: 'Job failed' } });
  };
}

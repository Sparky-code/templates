import { existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Db } from '../src/db.ts';
import { acquireLock, LockedError, ntfyNotifier, runJob } from '../src/job.ts';
import { testDb } from './db.ts';

let dir: string;
let db: Db;

beforeEach(async () => {
  ({ db, dir } = await testDb());
  process.exitCode = 0;
});

afterEach(async () => {
  await db.$disconnect();
  process.exitCode = 0;
});

describe('acquireLock', () => {
  it('refuses a lock held by a live process and takes over a stale one', () => {
    const path = join(dir, 'run.lock');
    const release = acquireLock(path);
    expect(() => acquireLock(path)).toThrow(LockedError);
    release();
    expect(existsSync(path)).toBe(false);

    writeFileSync(path, '999999999'); // no such process
    acquireLock(path)();
  });
});

describe('runJob', () => {
  it('records a successful run', async () => {
    const ok = await runJob('demo', async ({ max }) => `handled ${max}`, {
      db,
      lockPath: join(dir, 'run.lock'),
      dryRun: true,
      max: 3,
      log: () => {},
    });
    expect(ok).toBe(true);
    const [run] = await db.run.findMany();
    expect(run).toMatchObject({ job: 'demo', ok: true, dryRun: true, detail: 'handled 3' });
    expect(existsSync(join(dir, 'run.lock'))).toBe(false);
  });

  it('records a failure, notifies, and sets a non-zero exit code', async () => {
    const notify = vi.fn(async () => {});
    const ok = await runJob(
      'demo',
      async () => {
        throw new Error('upstream down');
      },
      { db, lockPath: join(dir, 'run.lock'), dryRun: false, max: 1, notify, log: () => {} },
    );
    expect(ok).toBe(false);
    expect(process.exitCode).toBe(1);
    expect(notify).toHaveBeenCalledWith('demo failed: upstream down');
    const [run] = await db.run.findMany();
    expect(run).toMatchObject({ ok: false, detail: 'upstream down' });
  });
});

describe('ntfyNotifier', () => {
  it('is disabled without a URL and posts the message with one', async () => {
    expect(ntfyNotifier('')).toBeUndefined();
    const fetchFn = vi.fn(async () => new Response('ok'));
    await ntfyNotifier('https://ntfy.example/topic', fetchFn)?.('boom');
    expect(fetchFn).toHaveBeenCalledWith(
      'https://ntfy.example/topic',
      expect.objectContaining({ method: 'POST', body: 'boom' }),
    );
  });
});

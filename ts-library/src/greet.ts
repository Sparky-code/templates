// Example module. Anything environment-specific (fetch, the clock, timers) is
// passed in rather than imported, so the library runs anywhere and tests can
// substitute it.

export interface GreetOptions {
  /** Defaults to the real clock; pass a fixed one in tests. */
  now?: () => Date;
}

/** Returns a greeting for `name` that depends on the time of day. */
export function greet(name: string, { now = () => new Date() }: GreetOptions = {}): string {
  const trimmed = name.trim();
  if (!trimmed) throw new RangeError('name must not be empty');
  const hour = now().getHours();
  const part = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
  return `Good ${part}, ${trimmed}`;
}

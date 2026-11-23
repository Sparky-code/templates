import { describe, expect, it } from 'vitest';
import { greet } from '../src/index.ts';

const at = (hour: number) => () => new Date(2026, 0, 1, hour);

describe('greet', () => {
  it('uses the time of day', () => {
    expect(greet('Ada', { now: at(9) })).toBe('Good morning, Ada');
    expect(greet('Ada', { now: at(14) })).toBe('Good afternoon, Ada');
    expect(greet('Ada', { now: at(20) })).toBe('Good evening, Ada');
  });

  it('trims the name and rejects an empty one', () => {
    expect(greet('  Ada ', { now: at(9) })).toBe('Good morning, Ada');
    expect(() => greet('   ')).toThrow(RangeError);
  });
});

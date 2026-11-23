/// <reference types="node" />
// Fails (exit 1) if tokens.ts has drifted from tokens.css.
// Usage: node design/check-tokens.ts [dir]   (defaults to this file's folder)
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const dir = resolve(process.argv[2] ?? dirname(fileURLToPath(import.meta.url)));
const css = readFileSync(join(dir, 'tokens.css'), 'utf8');
const { colors, space, type, rounded, duration } = (await import(
  pathToFileURL(join(dir, 'tokens.ts')).href
)) as typeof import('./tokens.ts');

const errors: string[] = [];

function block(selector: string): Map<string, string> {
  const start = css.indexOf(selector);
  if (start < 0) throw new Error(`tokens.css has no block for ${selector}`);
  const body = css.slice(css.indexOf('{', start) + 1);
  const vars = new Map<string, string>();
  for (const line of body.slice(0, body.indexOf('}')).split('\n')) {
    const m = line.match(/^\s*--([\w-]+):\s*(.+?);/);
    if (m?.[1] && m[2]) vars.set(m[1], m[2]);
  }
  return vars;
}

function oklchToRgb(value: string): [number, number, number] {
  const m = value.match(/oklch\(([\d.]+)\s+([\d.]+)\s+([\d.]+)\)/);
  if (!m) throw new Error(`not an oklch() colour: ${value}`);
  const [L, C, h] = [Number(m[1]), Number(m[2]), (Number(m[3]) * Math.PI) / 180];
  const a = C * Math.cos(h);
  const b = C * Math.sin(h);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const mm = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const lin = [
    4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * mm + 1.707614701 * s,
  ];
  const enc = (x: number) => {
    const c = Math.min(1, Math.max(0, x));
    return Math.round(255 * (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055));
  };
  return [enc(lin[0] ?? 0), enc(lin[1] ?? 0), enc(lin[2] ?? 0)];
}

function hexToRgb(hex: string): [number, number, number] {
  const n = Number.parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

const root = block(':root {');
const themes = { light: root, dark: block(':root[data-theme="dark"]') } as const;
for (const theme of ['light', 'dark'] as const) {
  const expected = themes[theme];
  for (const [role, hex] of Object.entries(colors[theme])) {
    const cssValue = expected.get(role);
    if (!cssValue) {
      errors.push(`${theme}.${role}: missing from tokens.css`);
      continue;
    }
    const want = oklchToRgb(cssValue);
    const got = hexToRgb(hex);
    if (want.some((v, i) => Math.abs(v - (got[i] ?? 0)) > 1)) {
      errors.push(`${theme}.${role}: tokens.ts ${hex} does not match ${cssValue}`);
    }
  }
}

const px = (name: string) => Number.parseFloat(root.get(name) ?? 'NaN');
for (const [k, v] of Object.entries(space)) {
  if (px(`space-${k}`) !== v) errors.push(`space.${k}: ${v} vs ${root.get(`space-${k}`)}`);
}
for (const [k, v] of Object.entries(rounded)) {
  if (px(`rounded-${k}`) !== v) errors.push(`rounded.${k}: ${v} vs ${root.get(`rounded-${k}`)}`);
}
for (const [k, v] of Object.entries(duration)) {
  if (px(`duration-${k}`) !== v) errors.push(`duration.${k}: ${v} vs ${root.get(`duration-${k}`)}`);
}
for (const [k, v] of Object.entries(type)) {
  if (px(`type-${k}-size`) !== v.size || px(`type-${k}-line`) !== v.line) {
    errors.push(`type.${k}: size/line differ from tokens.css`);
  }
  if (root.get(`type-${k}-weight`) !== v.weight) errors.push(`type.${k}: weight differs`);
}

if (errors.length) {
  console.error(`tokens.ts has drifted from tokens.css:\n  ${errors.join('\n  ')}`);
  process.exit(1);
}
console.log('tokens.ts matches tokens.css');

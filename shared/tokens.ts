// Design tokens for React Native, mirroring tokens.css (React Native has no
// CSS variables and no oklch(), so colours are the sRGB hex equivalents).
// Vendored from Sparky-code/templates; `node design/check-tokens.ts` fails if
// this file drifts from tokens.css.

export const space = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 24,
  6: 32,
  7: 48,
  8: 64,
  9: 96,
} as const;

export const type = {
  'display-large': { size: 57, line: 64, weight: '400' },
  'headline-large': { size: 32, line: 40, weight: '400' },
  'headline-medium': { size: 28, line: 36, weight: '400' },
  'title-large': { size: 22, line: 28, weight: '500' },
  'title-medium': { size: 16, line: 24, weight: '500' },
  'body-large': { size: 16, line: 24, weight: '400' },
  'body-medium': { size: 14, line: 20, weight: '400' },
  'label-large': { size: 14, line: 20, weight: '500' },
  'label-medium': { size: 12, line: 16, weight: '500' },
} as const;

export const rounded = { sm: 6, md: 10, lg: 16, full: 9999 } as const;

export const duration = { fast: 150, normal: 200, slow: 300 } as const;

export const colors = {
  light: {
    background: '#f9f8f6',
    surface: '#fefdfc',
    'surface-variant': '#efeeeb',
    border: '#d9d7d4',
    text: '#15151a',
    'text-muted': '#626369',
    primary: '#375587',
    'primary-hover': '#244172',
    'on-primary': '#f6f9fc',
    success: '#49814c',
    warning: '#cf9a35',
    danger: '#c53637',
  },
  dark: {
    background: '#0d0d0f',
    surface: '#161618',
    'surface-variant': '#1f1f22',
    border: '#323236',
    text: '#e9e8e4',
    'text-muted': '#97979e',
    primary: '#7ca5e9',
    'primary-hover': '#8eb8fe',
    'on-primary': '#07090d',
    success: '#7bc27e',
    warning: '#e9b452',
    danger: '#f97770',
  },
} as const;

export type ColorRole = keyof (typeof colors)['light'];

# Changelog

## [Unreleased]

## [0.1.0] - 2026-11-24

### Added

- Copier templates: baseline plus `ts-library`, `ts-cli`, `python-cli`, `python-service` and `react-web` shapes; baseline-only support for `expo`, `next` and `other`.
- `bin/new-project` to apply both layers, install and set up hooks.
- Shared design tokens (`tokens.css`, React Native `tokens.ts` with a drift check).
- Tests: rendering, the commit-msg hook, `copier update`, and end-to-end generation of every shape.

### Removed

- The cookiecutter Python CLI template (plate); it remains in the git history.

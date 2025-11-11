# Contributing Guide

Thanks for considering contributing! This project welcomes issues, feature proposals and pull requests.

## Branch Strategy

- `main`: Stable branch.
- `dev`: Active development.
- Feature branches: `feat/<short-name>`
- Fix branches: `fix/<short-name>`

## Pull Request Checklist

1. Code builds locally (Python & Node parts if modified).
2. No hard-coded secrets / API keys.
3. Added or updated minimal tests if logic changed.
4. Updated documentation (README / comments) if public behavior changed.
5. Follow Conventional Commits in messages: `feat: xxx`, `fix: yyy`, `docs: zzz`.

## Code Style

- Python: PEP8, consider running `flake8` / `black`.
- JS: Use ESLint (planned), keep functions small and descriptive.
- Avoid large monolithic HTML+JS; future refactor may split `Controller.html` scripts.

## Issues

- Use labels: `bug`, `enhancement`, `question`, `security`.
- Provide reproduction steps, expected vs actual behavior, environment info.

## Tests (Planned)

Add minimal tests for:

- LLM message construction (system prompt injection).
- Buffered transcript merge edge cases.
- Environment variable loading fallback.

## Security

If you discover a security issue DO NOT open a public issue(see SECURITY.md).

## Release Workflow

1. Merge features into `dev`.
2. QA / manual smoke test.
3. Update CHANGELOG.md.
4. Tag: `vX.Y.Z`.
5. Merge to `main`.

Thanks again! Your contributions help make this assistant better.

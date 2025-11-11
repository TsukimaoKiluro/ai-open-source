# Security Policy

## Supported Versions

Initial open-source release: v0.1.0 (preview). Future versions will list explicit support windows.

## Reporting a Vulnerability

Please DO NOT create a public issue for security problems.

## Disclosure

We aim for coordinated disclosure. Once fixed, we will publish details in CHANGELOG.md and optionally a dedicated advisory.

## Areas of Concern

- Hard-coded secrets / leaked environment variables
- XSS in Markdown rendering (now mitigated via DOMPurify)
- Rate limiting / abuse of LLM endpoint
- Injection into system prompt logic

## Planned Improvements

- Add Flask-Limiter for API rate limiting
- Add security scanning CI (Bandit / Dependabot)
- Automated dependency vulnerability checks

Thank you for helping keep the project safe!

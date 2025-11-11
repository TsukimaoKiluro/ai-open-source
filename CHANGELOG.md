# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0] - 2025-11-11

### Added

- Initial public open-source adaptation.
- Environment variable support for LLM API (removed hard-coded QINIU_API_KEY).
- `.env.example` added.
- MIT LICENSE.
- Security files: `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`.
- DOMPurify integration for safe Markdown rendering.
- Buffered transcript aggregation + inactivity timeout logic.
- Pseudo-streaming progressive AI reply rendering.

### Changed

- `llm_api.py` now refuses to start without `QINIU_API_KEY`.
- README updated with open-source caveats and quick start.

### Planned

- Real SSE streaming integration front-end.
- Rate limiting & CI workflows.
- Separation of large monolithic `Controller.html` into modular JS.

---

# MABOLO TECH — YouTube Auto Pilot

A Tamil-first, copyright-conscious content workflow for planning, scripting, rendering and publishing original YouTube videos.

## MVP status
- [x] Repository foundation
- [x] Tamil content draft generator (OpenRouter optional; offline fallback)
- [x] Daily GitHub Actions content-draft workflow
- [x] Automated tests
- [ ] Voice generation adapter
- [ ] FFmpeg video renderer
- [ ] YouTube OAuth upload integration
- [ ] Scheduled publishing and analytics

## Current channel direction
Initial editorial direction: **Tamil History & Ancient Mysteries**. Treat historical claims carefully: distinguish primary evidence, scholarly interpretation and folklore. Never present uncertain claims as established fact.

## Quick start
Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_content
```

Without an API key, the generator creates a clearly labelled starter draft from the local topic bank. To use an OpenAI-compatible provider such as OpenRouter, set `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL`.

## GitHub Actions
The daily workflow creates a content draft and uploads it as an artifact. Add `OPENROUTER_API_KEY` under repository **Settings → Secrets and variables → Actions** to enable AI-generated drafts. Do not put keys in source code or chat.

## YouTube publishing
Uploading requires Google OAuth 2.0 authorization with the `youtube.upload` scope and the YouTube Data API enabled. This project will default to **private/unlisted review**, not automatic public publishing, until the owner explicitly changes the setting and tests the full upload flow.

## Safety and quality
- Use original scripts, narration and visuals, or assets with verified licences.
- Do not reuse copyrighted footage/music without permission.
- Fact-check historical claims and cite sources in video descriptions.
- Add meaningful narration, analysis and editing; avoid mass-produced repetitive videos.
- Review every generated video before enabling public auto-publishing.

## Project structure
```
src/                  content generation
tests/                automated tests
content/topics.json   starter topic bank
output/               generated drafts (git-ignored)
.github/workflows/    scheduled automation
```

# MABOLO TECH — YouTube Auto Pilot

A Tamil-first workflow for creating original YouTube Shorts, with a review-first publishing approach.

## MVP status
- [x] Tamil topic bank and script draft generator
- [x] Optional OpenRouter-compatible AI script generation
- [x] Tamil text-to-speech adapter (Edge TTS)
- [x] SRT subtitle generation
- [x] Original generated Tamil-history themed background and thumbnail artwork
- [x] FFmpeg 1080×1920 vertical video rendering
- [x] Daily GitHub Actions workflow and artifact output
- [x] Unit tests for content, visuals and render command
- [ ] Long-form video assembly
- [ ] YouTube OAuth upload integration
- [ ] Analytics and performance feedback loop

## Editorial direction
Initial direction: **Tamil History & Ancient Mysteries**. Separate archaeological evidence, scholarly interpretation, literary tradition and folklore. Never present disputed claims as established fact.

## Local setup
Requires Python 3.11+, FFmpeg with the subtitles/libass filter, and a Tamil font such as Noto Sans Tamil.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_content
python -m unittest discover -s tests -v
python -m src.render_video
```

The render step uses the newest `output/tamil-draft-*.json` file by default. To render a particular draft:

```bash
python -m src.render_video --draft output/tamil-draft-YYYYMMDD-HHMMSS.json
```

The generated outputs include JSON draft, MP3 narration, SRT subtitles, a 1080×1920 background, a 1280×720 thumbnail and an MP4 Short. The artwork is original programmatically generated artwork, not a photograph or a claim to depict a specific archaeological site.

## AI provider
Without `OPENROUTER_API_KEY`, a clearly labelled offline starter draft is generated. To enable AI-assisted scripts, add `OPENROUTER_API_KEY` under repository **Settings → Secrets and variables → Actions**. Optionally set the repository variable `OPENROUTER_MODEL`. Never commit API keys or send them in chat.

## Daily automation
GitHub Actions is scheduled for 08:00 Asia/Kolkata. It creates a draft, runs tests, generates narration and visuals, renders a vertical video and stores the outputs as an artifact for 14 days. You can also run it manually from the Actions tab.

## YouTube publishing
The current workflow does **not** upload videos to YouTube. Uploading requires a Google OAuth 2.0 client, the YouTube Data API enabled, and authorization with the `youtube.upload` scope. The planned default is private review; public publishing must be explicitly enabled by the channel owner after testing.

## Copyright, factual accuracy and quality
- Use original scripts, narration and artwork or assets with verified licences.
- Do not use copyrighted footage/music without permission.
- Fact-check historical claims and include reliable source links in descriptions.
- Add meaningful narration, analysis and editing; avoid repetitive mass-produced uploads.
- Review each generated video before public publishing.
- Edge TTS is an online service; confirm its current terms and permitted use before monetized production.

## Project structure
```
src/                  content generation, visuals and rendering
tests/                automated tests
content/topics.json   starter Tamil topic bank
output/               generated files (git-ignored)
.github/workflows/    scheduled automation
```

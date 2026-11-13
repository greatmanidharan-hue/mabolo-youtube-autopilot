# MABOLO TECH — YouTube Auto Pilot

A Tamil-first workflow for creating original YouTube Shorts, with a review-first publishing approach.

## MVP status
- [x] Tamil topic bank and script draft generator
- [x] Optional OpenRouter-compatible AI script generation
- [x] Tamil text-to-speech adapter (Edge TTS)
- [x] SRT subtitle generation
- [x] Four original topic-matched scene illustrations per Short
- [x] FFmpeg 1080×1920 vertical slideshow rendering with narration and subtitles
- [x] Daily GitHub Actions workflow and artifact output
- [x] Three-topic rotating daily batch (distinct topics selected by date)
- [x] Review-first upload queue manifest with private-by-default status
- [x] Offline HTML preview gallery
- [x] Unit tests for content, visuals, render command and publishing safety
- [x] Editorial quality report distinguishes research leads from claim-level verification
- [ ] Long-form video assembly
- [x] Review-first YouTube OAuth upload CLI (manual credentials required)
- [ ] Analytics and performance feedback loop

## Editorial direction
Initial direction: **Tamil History & Ancient Mysteries**. Separate archaeological evidence, scholarly interpretation, literary tradition and folklore. Never present disputed claims as established fact.

## Local setup
Requires Python 3.11+, FFmpeg with the concat demuxer and subtitles/libass filter, ffprobe, and Noto Sans Tamil. Set `TAMIL_FONT_PATH` if the font is installed in a non-standard location.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.daily_batch --count 3
```

Each Short receives four original topic-matched illustrative scenes. The renderer divides the narration duration across those scenes and switches scenes through FFmpeg's concat demuxer. These are programmatic illustrations, not documentary photographs or depictions verified to be a specific archaeological site. Tamil subtitles use a smaller font, wide side margins, a bottom safe margin and automatic wrapping.

The output includes JSON draft, MP3 narration, SRT subtitles, four scene PNGs, thumbnail, MP4, quality report, review queue and `preview-index.html`. After downloading and extracting the Actions artifact, open the gallery. On Android, if sibling media links fail in the Files preview, use **Choose MP4 file** and select the matching MP4 from the extracted folder.

## AI provider
Without `OPENROUTER_API_KEY`, a clearly labelled offline starter draft is generated. To enable AI-assisted scripts, add `OPENROUTER_API_KEY` under repository **Settings → Secrets and variables → Actions**. Optionally set `OPENROUTER_MODEL`. Never commit API keys or send them in chat.

## Daily automation
GitHub Actions is scheduled for 08:00 Asia/Kolkata. It selects three different topics, creates drafts, runs tests, generates narration and four scene illustrations per topic, renders three vertical videos, writes an upload review manifest and preview gallery, then stores outputs as an artifact for 14 days. The queue does not upload or publish anything.

## Editorial quality gate
Source URLs are research leads only, not proof that claims were checked. Drafts start with `sources_verified: false` and an empty `claim_checks` list. Public upload is blocked unless a human has completed editorial review and claim-by-claim source verification. The quality report never auto-approves a draft.

## YouTube publishing
The current workflow does **not** upload videos to YouTube. Uploading requires a Google OAuth 2.0 client and the YouTube Data API. The local CLI defaults to private. Public publishing remains blocked until a human documents editorial approval and source verification.

## Copyright, factual accuracy and quality
- Use original scripts, narration and artwork or assets with verified licences.
- Do not use copyrighted footage/music without permission.
- Fact-check historical claims against reliable publications.
- Review every generated video before public publishing.
- Edge TTS is an online service; confirm its current terms before monetized production.

## Project structure
```
src/                  content generation, visuals and rendering
tests/                automated tests
content/topics.json   starter Tamil topic bank
output/               generated files (git-ignored)
.github/workflows/    scheduled automation
```

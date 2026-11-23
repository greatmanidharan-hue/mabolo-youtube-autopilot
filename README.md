# MABOLO TECH — Simple Tamil Viral Topic Autopilot

A review-first workflow that discovers popular YouTube topics across selected countries and creates a **new, original Tamil Short** about the same broad subject.

## Workflow
1. Read public popularity metadata from YouTube's official Data API.
2. Rank candidate topics using views-per-hour and engagement as a heuristic.
3. Write a fresh Tamil script with OpenRouter.
4. Generate new Tamil voiceover and subtitles with Edge TTS.
5. Create original non-3D illustrative visuals and assemble a vertical video with FFmpeg.
6. Save the draft, metadata, quality report and preview for human review.

## Copyright and monetization safeguards
- Never download or reuse another creator's video, audio, transcript, thumbnail, logo or distinctive branding.
- Do not translate or closely paraphrase the source video's script. Use original wording, structure and explanation.
- Use original visuals or assets with a verified commercial-use licence. Current visuals are simple original illustrations, not documentary photographs.
- Verify the TTS provider's current commercial-use terms before monetizing.
- A trend URL and metadata are discovery leads, not factual sources. Verify every factual claim using reliable sources.
- Outputs remain review-required and private by default. Nothing is automatically uploaded or published.
- These safeguards reduce risk but cannot guarantee monetization. Follow YouTube's current originality, reused-content, copyright and advertiser-friendly policies.

## GitHub Actions secrets
Add repository secrets under Settings → Secrets and variables → Actions:
- `YOUTUBE_API_KEY`: Google API key with YouTube Data API v3 enabled.
- `OPENROUTER_API_KEY`: API key for original Tamil script generation.

Optional variable: `OPENROUTER_MODEL` (defaults to `openai/gpt-4o-mini`).
Trend discovery currently compares popular-video metadata across selected regions: US, GB, CA, AU, JP, KR, IN, DE and BR. This is a popularity heuristic, not a definitive viral ranking.

The workflow runs daily at 08:00 Asia/Kolkata and can be started manually. It creates one Short per run. If a required secret is missing, it stops with a clear error rather than silently using an unrelated topic-bank draft.

## Local setup
Requires Python 3.11+, FFmpeg, ffprobe, Noto Sans Tamil, and both API keys.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.daily_batch --count 1
```

Outputs include script JSON, MP3 narration, SRT subtitles, scene PNGs, MP4, quality report, private review queue and HTML preview.\n\n## Reference shot analysis (user-owned/licensed clips only)\n\n```bash\npython -m src.analyze_reference --input path/to/your-authorized-reference.mp4\n```\n\nThis extracts scene-change frames and writes a timestamped `*-shot-plan.json` under `output/reference_analysis/`. It does not generate replacement characters or final video yet; the current renderer still uses abstract placeholder illustrations. The next integration step is a video-generation provider that consumes the shot plan and produces new Indian-character shots.

## Publishing
The workflow does not publish to YouTube. Review the script, claims, asset licences and finished video first. Use the existing manual OAuth upload process only after approval. Public publishing remains blocked until human review and claim verification are complete.

## Intentionally out of scope
Blender, 3D characters, character animation, lip-sync and paid cinematic video generation.

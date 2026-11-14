# Keeladi pilot — free local Blender render

1. Install Blender 4.x from https://www.blender.org/download/.
2. Open PowerShell in the repository root.
3. Run: blender -b -P scripts/blender/keeladi_pilot.py
4. Find the silent vertical animation at output/keeladi-pilot-visual.mp4.

The script creates four original 3D story sets: dawn settlement, pottery, household craft/weaving, and a shared water point. It uses procedural Blender meshes, keyframed wheel/arm motion, camera cuts, warm lighting and an H.264 vertical render.

This first version is a free proof of concept. It does not yet include detailed facial rigging, realistic walk cycles, lip-sync or documentary-accurate reconstruction. Add Tamil narration/subtitles using the existing project pipeline after reviewing the silent render.

No Runway, Higgsfield, paid AI video model or credit-consuming generation is used.


## High-detail character study preview

A separate full-body stylized ancient Tamil woman character concept is available in `keeladi_character_study.py`. It is a standalone modeling study and does not change the existing four-scene pilot.

From the repository root, run:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P scripts\blender\keeladi_character_study.py
```

The single PNG preview is written to `output/keeladi-character-study.png`. Review this still before attempting another long animation render. The model is procedural and intended as a free stylized character-design prototype; it is not yet a production rig or a claim of feature-film asset quality.

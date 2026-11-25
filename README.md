# Selvática Residences: interactive tower walkthrough

A single-page, no-build website (plain HTML, CSS and JavaScript) for **Selvática Residences** by **Privé Real Estate**.
Nothing is rendered in 3D. The page only plays and scrubs short video clips and fades between still renders.

Open `site/index.html` through any static web server (videos and `availability.json` do not load from `file://`).

```bash
cd site && python3 -m http.server 8765
```

## What the visitor can do

| Step | What happens |
| --- | --- |
| Front screen | Hover any level of the tower: a soft gray glass band lights that level and the glass card on the right shows its number, plan and availability. The card opens on level 7. |
| Click the **rooftop** (top level) | Clip 1 pushes in to the top of the tower, clip 2 swings to the corner view of the rooftop amenities. **Back** (or Esc) plays it in reverse. |
| **Show top view** (on the corner view) | Clip 3 tips the view straight down onto the plan. The **Top floor** plan shows first, with a **Main floor / Top floor** switch (cross-fade). Hover an area to see its name. **Back to corner view** reverses it (from the main floor it settles on the top floor first). |
| Click **level 30** | Clip 1 pushes in, then clip 6 redraws the building as a sketch and lifts the level into its 3D floor plan. **Back** reverses it. |

## Files

```
site/
  index.html          the whole page (HTML + CSS + JS in one file)
  availability.json   which units are NOT available, per level (edit this by hand)
  building.webp       the front elevation of the tower (hover layer and hub picture)
  logo_prive.png      Privé Real Estate logo (top left)
  logo_selvatica.png  Selvática Residences logo (headline block)
  plan_main.webp      top-view render, main amenity floor
  plan_top.webp       top-view render, top amenity floor
  stage1.mp4          clip 1: full tower to the top of the tower        (1080p, 3 s)
  stage2.mp4          clip 2: top of the tower to the rooftop corner view (1080p, 3 s)
  stage3.mp4          clip 3: corner view to the straight-down top view   (1080p, 4 s)
  stage6.mp4          clip 6: top of the tower to the level 30 3D plan    (720p enlarged, 6 s)
tools/                helper scripts used while making the clips (see below)
.github/workflows/pages.yml   GitHub Pages deployment
```

Clips are encoded for scrubbing: H.264, no audio, keyframe every 6 frames, `-movflags +faststart`.

## Editing without touching images

**Unit availability.** Open `site/availability.json`. Each level lists the unit numbers (1 to 9) that are *not* available:

```json
"21": [1, 5]
```

Any unit that is not listed is available. Levels 6 to 32 share the same plan (the plan outlines were traced from the supplied floor plan image and live inside `index.html` as `PLAN`).
The values in the file now are **random placeholders** (2 or 3 per level).

**Settings at the top of the script in `index.html`:**

| Name | What it does |
| --- | --- |
| `RATE` | Playback speed of the rooftop flight (3.2 = about 2 s). |
| `RATE3`, `RATE5` | Speed of the top-view clip and of the level 30 clip. |
| `DEFAULT_LEVEL` | Level the card shows before anything is hovered (7). |
| `FLOOR_LEVEL` | The level that opens the 3D plan (30). |
| `COUNT`, `TOP`, `PITCH`, `X0`, `X1` | The hover grid laid over `building.webp`. Add `?grid` to the URL to see every band. |
| `TIERS` | Names, copy, sizes and bedrooms shown on the card for levels 6 to 32. |
| `REGIONS` | Hover areas and their names for the two top-view plans (plan pixels, 1670 x 942). |

**Test hooks (URL):** `?grid` shows the level bands, `?view=top` opens straight on the top view, `?at=0.5` freezes the rooftop flight at that point.

## Placeholders still to replace

- Headline copy under the Selvática logo, the card copy (`TIERS`), elevation, sizes, bedrooms and prices.
- The three figures bottom left: 37 levels, 432 units, 47 amenities. The card counts to /33, because the render shows 33 levels including the roof. These need to agree.
- `availability.json` values (random).
- Top-view area names come from the labelled amenity plans; their outlines were drawn by eye and may need nudging.
- Floor plan: only level 30 opens a 3D plan; floors 1 to 5 show "Plan to follow".
- Floor plans, Available units and booking actions are not built yet (the side menu was removed).

## Regenerating a clip

Clips were made with Higgsfield (`cinematic_studio_video_v2`, `std`, `sound off`, `speedramp linear`, 16:9, `cfg_scale` 0.85), always with a start frame **and** an end frame, chained from the real last frame of the previous clip. Previews at 720p; the approved clip is upscaled to 1080p (Topaz). Re-encode with:

```bash
ffmpeg -i in.mp4 -vf scale=1920:1080:flags=lanczos -an -c:v libx264 -preset slow -crf 22 \
  -g 6 -keyint_min 6 -sc_threshold 0 -pix_fmt yuv420p -movflags +faststart out.mp4
```

`tools/audit_clip.py CLIP START_STILL END_STILL OUT_PREFIX` checks start/end match, jumps and sharpness and writes a contact sheet; `tools/walk.py CLIP...` scores camera steadiness (lower is steadier); `tools/trace_plan.py` traced the unit outlines; `tools/edge_ratio.py` measures dark edges in a screen recording.

## Working together

**Always `git pull` before editing `index.html`.** It is one large file, and publishing from an old copy silently replaces newer work.
Do not force-push. If the remote has newer commits, fetch and merge.

## Deployment (GitHub Pages)

`.github/workflows/pages.yml` publishes the `site/` folder on every push to `main` (or by hand from the Actions tab). One-time setup in the repository: **Settings, Pages, Source: GitHub Actions**. A 25 second wait between upload and deploy avoids a known "artifact not found" failure.

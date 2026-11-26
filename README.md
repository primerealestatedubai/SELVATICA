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
| Hover the spot by the **fire pit** (rooftop corner view) | A glass label says "Click to explore". Clicking glides the camera down to the terrace and spiral staircase (clip 7). On that view, **scrolling** (wheel, touch drag or arrow keys) turns the camera to the infinity pool (clip 8). **Back** eases the scroll to the start, then reverses clip 7. |
| Hover **level 30**, then click **unit 8** in the card's map | Clip 1 pushes in to the top of the tower, then one joined clip (`stage12`) goes straight in at the facade centre, through the closed glass into a living room and zooms out onto the 110 m² plan on white. It plays as one move (about 3 s) and stops on the plan. **Back** reverses it. |
| **Scroll** on the plan | Walks through the apartment: 20 clips, plan > living > dining > balcony > kitchen > living > hallway > master bedroom > closet > ensuite > hallway > second bedroom > shared bathroom > living > plan. Scroll back to go back; **Back** eases the scroll to the start, then reverses the flight. Wheel, touch drag and arrow keys work; Space / Page Down glides to the next clip. |

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
  stage7.mp4          clip 7: rooftop corner view to the terrace / staircase (1080p, 5 s)
  stage8.mp4          clip 8: terrace to the pool, scrubbed by scrolling   (720p enlarged, 5 s)
  stage12.mp4         unit 8 flight: facade centre, through the glass, living room, plan on white (1080p, 8.8 s)
  walk1.mp4 ..3       the apartment walkthrough, 720p (1280 x 720), 3 files so each stays small; see below
tools/                helper scripts used while making the clips (see below)
.github/workflows/pages.yml   GitHub Pages deployment
walkthrough_720p/     the walkthrough as delivered: selected clips, assembled master, generation report
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
| `RATE3` | Speed of the top-view clip. |
| `FLY1`, `FRATE`, `FEND` | Speed of clip 1 on the unit 8 journey, of the joined clip, and the speed it eases down to as the plan settles. |
| `WALK_PX` | Scroll distance per second of walkthrough footage (110; the whole walkthrough is about 128 s). |
| `RATE6` | Speed of the terrace glide (4.2 = about 1.2 s). |
| `SCROLL_PX` | Wheel distance for the whole pool clip (1500). |
| `SPOT` | Centre and size of the fire pit hover spot, as fractions of the rooftop picture. |
| `DEFAULT_LEVEL` | Level the card shows before anything is hovered (7). |
| `FLOOR_LEVEL`, `FLOOR_UNIT` | The level and unit whose click opens the plan and the walkthrough (30, 8). |
| `COUNT`, `TOP`, `PITCH`, `X0`, `X1` | The hover grid laid over `building.webp`. Add `?grid` to the URL to see every band. |
| `TIERS` | Names, copy, sizes and bedrooms shown on the card for levels 6 to 32. |
| `REGIONS` | Hover areas and their names for the two top-view plans (plan pixels, 1670 x 942). |

**Test hooks (URL):** `?grid` shows the level bands, `?view=top` opens straight on the top view, `?at=0.5` freezes the rooftop flight at that point.

## Placeholders still to replace

- Headline copy under the Selvática logo, the card copy (`TIERS`), elevation, sizes, bedrooms and prices.
- The three figures bottom left: 37 levels, 432 units, 47 amenities. The card counts to /33, because the render shows 33 levels including the roof. These need to agree.
- `availability.json` values (random).
- Top-view area names come from the labelled amenity plans; their outlines were drawn by eye and may need nudging.
- Floor plan: only level 30, unit 8 opens a plan and the walkthrough; floors 1 to 5 show "Plan to follow".
- Floor plans, Available units and booking actions are not built yet (the side menu was removed).
- Clip 8 is 720p enlarged to 1920x1080; upscale it to 1080p for full sharpness. The walkthrough is deliberately 720p.
- The pool view (end of the scroll) is the last stop so far; more clips are to follow.

## The apartment walkthrough (720p)

Made from the 15 approved stills (`01`..`15`) with Higgsfield `cinematic_studio_video_v2`, 1280 x 720, start and end image per clip, no upscaling. The timeline is

```text
01 > 02 > 03 > 04 > 05 > 06 > 07 > 08 > 09 > 10 > 11 > 10 > 12 > 10 > 13 > 14 > 13 > 15 > 13 > 02 > 01
```

Sixteen clips were generated (C01 to C10, C12, C14, C15, C17, C19, C20). The four returns C11, C13, C16 and C18 are the outbound clips C10, C12, C15 and C17 played backwards (checked: it backs out along the same path, the door swings shut, and the endpoints are exact). On the page, the clips sit one after another inside `walk1.mp4` to `walk3.mp4`, and the list of ranges (the `WALK` object near the top of the script) says where each clip starts and ends and which ones play backwards. `tools/build_walk.py` rebuilds the three files and that list from the selected clips. `walkthrough_720p/generation-report.txt` lists every clip's endpoints, attempts, the attempt chosen and any open defects.

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

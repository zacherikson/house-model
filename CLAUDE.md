# House model — notes for Claude

(The live page's title is "New House" — changed by the owner or another session on 2026-11-26; keep it.)

Read this first. It is the hand-off between sessions so the owner never has to re-explain the project.

## What this is
A walk-through 3D model of the owner's house, viewable in a web browser on laptop and phone. Built with three.js, published as a private claude.ai artifact:

- **Live page:** https://claude.ai/artifact/EFu2P1JBHXwLYxYHmmqgfk (republish with the Artifact tool, `url` = that link,
  page = `site/index.html`, files = `house.json` and `tex/*.jpg` mapped to `site/house.json`, `site/tex/...`).
  Read the artifact first in a new session; the publish is refused otherwise. The Artifact tool only reads files inside
  the session's working directory or scratchpad, so copy `site/index.html` and `site/house.json` there before publishing.

- **GitHub Pages:** `.github/workflows/pages.yml` builds `_site/` with `pipeline/mkpages.py` (adds the HTML skeleton the
  artifact host normally supplies, copies house.json + tex/) and deploys on every push to main, to
  https://zacherikson.github.io/house-model/ — needs the repo public (or a paid plan) and Settings → Pages → Source =
  "GitHub Actions". Keep both the artifact and Pages working: edit `site/index.html` in artifact form (no doctype/head).

## How the owner wants to work (from their original brief — follow it)
- Realism over simplicity: should look like a photo of a real home, not blocks. Use real 3D models for furniture and
  fixtures and real photographed materials; when the exact piece can't be found, use the closest match and say so.
- **Plans are the source for structure. Photos are the source for everything else, and photos win** when they disagree.
- **Don't invent things to fill gaps.** If something can't be told from plans/photos, ask — and gather questions into
  ONE list rather than one at a time.
- Owner is not technical. Keep it one link that just opens; it must run smoothly on a phone. Do any setup yourself.
- Just the house and yard. No neighbors.
- Check work against the photos before showing; say what you're unsure of.
- Later they want design ideas (furniture, lighting, yard). **Ideas must stay clearly separate from what's real**
  — see `ideas/README.md`.
- Owner originally asked to build one room 2–3 ways (baked lighting / live lighting / photo-scan) and compare against
  their photo before doing the whole house. They then chose to see a plans-only version first. That comparison is still
  owed once photos arrive.
- Owner preference: lead with the direct answer, no preamble.

## Current state (as of 2026-11-26)
- Main floor + basement + exterior built **from plans only**. No photos received yet. All finishes are placeholders and
  the page says so ("What's real?" sheet lists from-plans / assumed / placeholder).
- No furniture, interior doors, mirrors or light fixtures yet.
- **This repo is public. Never commit the plans PDF, photos, the address, lot/subdivision, client or builder names.**
  The plans PDF (`source/plans/plans-review-set-2026-06-02.pdf`) and photos (`source/photos/`) are gitignored; if they
  are not on disk, ask the owner to upload them (or keep them in a private place such as a Google Drive folder).
- Source plans: a "Review Set, Not for Construction" dated 2026-06-02. Contains only sheets 2, 3, 4, 5, 8
  (elevations, roof birdseye, foundation/basement, main floor, plot plan). Sheets 1, 6, 7 missing.

## Open questions for the owner (ask as one list when relevant)
1. Is the house built and furnished? Did anything change from the June 2026 review set? Is there a final set?
2. Missing sheets 1, 6, 7 (sections, electrical/lighting?), cabinet drawings, builder selections sheet (flooring,
   counters, cabinets, paint, fixture model numbers).
3. Any vaulted ceilings? (Model assumes flat 10' main, 8'-8" basement.)
4. What is the unlabeled walled rectangle under the back patio on the foundation sheet? (Treated as solid fill.)
5. Does the front roof dormer window light a room? (Dormers omitted.)
6. Yard: how much of the lot, plus driveway/fence/patio/plantings not on the plot plan.
7. Which phone/laptop (performance target).
8. Photos: each room from the corners, close-ups of materials, each furniture piece (+brand/model if known),
   exterior from all sides, yard; optional video or Scaniverse scan of the test room.

## Assumptions baked into the model (change when evidence arrives)
- Main floor at 0; yard and garage slab at −24" (front porch has 3 risers). Basement floor −128", ceiling −24".
  Basement stair: 16 risers of 8".
- Window/door heads at 96" on the main floor; basement window heads at −28" with wells.
  Unlabeled interior openings run to the ceiling.
- Roof simplified from the birdseye sheet (8:12; porch shed 3:12). Gables: left-front wing, entry, garage front,
  back patio.
- Back patio slab x 258–520, y −50…120 (from foundation sheet + "DN" steps). Porch posts at x 49/248/345.
- Garage "12' shoe shelves" placed along the laundry wall inside the garage; office bookshelf on the garage wall.
- Upper kitchen cabinets where the plan shows dashed lines.

## Coordinates and units
- Everything is in **inches in plan space**: x = right on the main-floor sheet (= **west**), y = down on the sheet
  (= **north**, toward the road). Height h: main floor = 0. World (three.js) = inches × 0.0254 m, x→x, y→z, h→y.
- Plan scale is exactly 1/8" = 1' (0.75 pt per inch). Basement sheet is shifted by (dx, dy) = (2, 78) inches
  relative to the main sheet (found by cross-correlating wall masks; overlay matched within ~1").

## Pipeline (`./build.sh` regenerates `site/house.json`, verified byte-identical)
1. `pipeline/walls.py` — rasterizes the 0.48pt black wall outlines (2 px/inch), fills thin enclosed regions → wall mask.
   `walls_b.py` does the foundation sheet and adds the grey hatch as foundation walls.
2. `openings.py` — reads door/window labels (e.g. 3050SH = 3'0"×5'0" single-hung; rotated labels are reversed text),
   finds the matching gap in the wall mask by size and position.
3. `export.py` — decomposes walls into rectangles, flags exterior sides, flood-fills rooms and names them from labels.
   Hand fixes live in `pipeline/fixes/*.json` (`fill` = add wall, `hole` = remove floor, e.g. the stairwell).
4. `combine.py` — merges both floors, drops garage foundation walls and the patio fill from the basement, computes the
   lawn with a cut-out for the basement and window wells.
5. Built-ins (cabinets, fixtures, porch, roof, stairs) are hand-placed in `site/index.html` from the plan drawing;
   coordinates are commented there.

## Viewer (`site/index.html`)
- Single page; three.js 0.170.0 + addons loaded from jsDelivr via importmap (allowed by the artifact CSP). Textures:
  wood + grass from three.js examples (placeholders); everything else procedural canvas textures.
- Two collision/floor grids (`G` main, `GB` basement, 2" cells). Step-up limit 10" (look-ahead 18"); after 0.4 s stuck,
  allows 40" so nobody gets trapped. Level switches at floor −64" on the stair.
- Layers: main, ceil, roof, bsmt, bceil, site — Overview hides ceilings, toggles roof and basement.
- Owner asked for high quality always (ambient occlusion + 4096 shadows on every device, no toggle) and a round "?"
  button for the What's-real sheet.
- `window.__view` / `window.__dbg` exist for automated screenshots and walk tests.

## Testing
- `python3 pipeline/mktest.py site/index.html <dir>/index.html` writes a copy that loads three.js from `./lib/`
  (copy `node_modules/three/build/three.module.min.js` → `lib/`, `examples/jsm` → `lib/jsm`; `npm i three@0.170.0`).
  Serve that dir on :8765 (with house.json and tex/) and run `node tests/walktest.js` (stairs, doors, patio, garage),
  `node tests/pits.js` (trap scan), `node tests/coplanar.js` (surfaces sharing a plane = flicker; what remains
  after the stair fix is hidden inside walls/behind cabinets/underground — re-run after adding geometry), `node tests/shoot2.js <outdir> '<views json>'` (screenshots).
  Headless Chromium uses SwiftShader; it is slow but works. Not yet tested on a real phone.

## Bugs fixed so far (don't regress)
- Lawn used to run under the house and showed in the stairwell → lawn now has a basement cut-out.
- Doorways had floor gaps (fell to −24 and got stuck) → thresholds added after room floors; anti-stuck rule.
- A leftover garage floor rect covered the hallway outside the garage door → removed.
- Roof soffits/fascia used to show inside rooms → eaves sit above the 10' ceiling.
- East basement closet had no end wall (the garage filter in combine.py dropped it) → filter now starts at y>205.
- White flicker on floors at doorways (overlapping coplanar floors) → room floors tuck only 1" under walls and door
  thresholds are trimmed to meet them edge to edge; camera near plane 0.1 m.
- Stairs flickered while moving (risers shared the tread tops; stairwell edges sat on the floor/ceiling planes) and
  the same issue hit basement ceilings under main walls, garage floor edges, cold storage, tub/shower tile and window
  reveals → risers stop under the tread above; walls/slabs have no bottom faces; tile sits on the true wall faces;
  exterior trim laps 1/2" into openings. The family-room firebox was hidden inside the plan's 4" firebox wall → moved
  to its face. Rule: never put two faces on the same plane facing the same way.

## Next steps
- Owner's photos → real finishes and furniture; then the 2–3-way room comparison (baked lighting / live / scan).
- Ideas system (`ideas/`), interior doors, light fixtures, mirrors, yard.

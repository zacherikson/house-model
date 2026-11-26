# New House — 3D walk-through

**Open it:** https://claude.ai/artifact/EFu2P1JBHXwLYxYHmmqgfk — works in a browser on a laptop or phone.

- **Walk:** W A S D or arrow keys and drag to look (laptop); left circle to walk and drag to look (phone).
- **Overview:** dollhouse view from above. **Roof** and **Basement** buttons show or peel away floors.
- **Go to…** jumps to any room. **Sun** sets the time of day. **What's real?** lists what came from the plans,
  what was assumed, and what is a placeholder.

Right now the model is built only from the house plans (kept private, not in this repository). Colors, floors, counters, cabinets, siding and
fixtures are placeholders until photos are added.

## What's in this folder
| Folder | What it holds |
|---|---|
| `site/` | The page itself (what the link shows) and its data and textures |
| `source/` | Kept off GitHub on purpose: the plans PDF and your photos stay private (see `source/README.md`) |
| `ideas/` | Design ideas, kept separate from the real house |
| `pipeline/` | Scripts that read the plans and produce the house layout |
| `tests/` | Automated walk-through and screenshot checks |
| `CLAUDE.md` | Notes so the next Claude session can pick up where this one left off |

# ARCHITECTURE.md

## What I Built and Why

**Stack: Python + Streamlit + Plotly**

Streamlit was the right call for this use case for three reasons: (1) it requires zero frontend code — the entire tool is a single Python file, (2) it deploys for free in minutes on Streamlit Cloud with a shareable public URL, and (3) Plotly integrates natively and handles interactive map overlays, heatmaps, and hover states with minimal code. For a Level Designer audience — not data scientists — a clean, interactive browser tool matters more than technical elegance under the hood.

---

## Data Flow

```
player_data/
  February_10/ ... February_14/
        │
        ▼
  PyArrow reads each .nakama-0 file as Parquet
        │
        ▼
  Pandas DataFrame per file → concat into master df
        │  (cached with @st.cache_data — runs once per session)
        │
        ▼
  Decode event bytes → classify is_bot by user_id shape
        │
        ▼
  World (x, z) → pixel (px, py) via coordinate formula
        │
        ▼
  Streamlit sidebar filters (map / day / match / events)
        │
        ▼
  Plotly figures rendered:
    - Journey view: scatter + line traces over minimap
    - Heatmap: 2D histogram → gaussian blur → Plotly Heatmap trace
    - Timeline: filtered by time window slider → current positions
    - Stats: bar, pie, area, table charts
```

---

## Coordinate Mapping Approach

This was the trickiest part. The game uses a 3D world coordinate system (x, y, z). For 2D minimap plotting:

- **y is elevation** — ignored entirely for plotting
- **x and z** are the two horizontal axes

Each map has a **scale** (world units per minimap) and an **origin** (world coordinate of the minimap's bottom-left corner). The conversion:

```python
u = (x - origin_x) / scale          # 0..1 normalized
v = (z - origin_z) / scale          # 0..1 normalized
pixel_x = u * 1024
pixel_y = (1 - v) * 1024            # flip: image Y=0 is top, world Z increases upward
```

The Y-flip is the key insight. Minimap images have (0,0) at top-left; the game world has Z increasing "upward" on the map. Without the flip, all coordinates appear mirrored vertically.

---

## Assumptions Made

| Situation | Assumption |
|-----------|-----------|
| Bot detection | A `user_id` that parses as a pure number is a bot; UUIDs are humans. Per README spec. |
| match_id | Strip `.nakama-0` suffix for display (it's a server instance tag, not part of the match identity) |
| Timestamps | Use relative time within a match (subtract match t_min) for playback; wall-clock time is not meaningful |
| February 14 | Treated as a partial day — no special handling needed, just fewer records |
| Missing map_id | Rows with map_id not in the 3 known maps are dropped (none observed in practice) |
| Heatmap smoothing | Gaussian sigma=20px chosen empirically for readable density at 1024px map size |

---

## Trade-offs

| Decision | What I chose | What I gave up | Why |
|----------|-------------|----------------|-----|
| Data loading | Load all files at startup, cache | Memory usage (~500MB) | Instant filter response after first load |
| Heatmap rendering | Server-side numpy → Plotly | GPU-accelerated WebGL | Simpler, no WebGL dependencies |
| Timeline playback | Slider scrub (not auto-play) | Animated playback button | Reliable across all browsers, no JS needed |
| Match display limit | Cap sidebar at 50 matches | Full match search | Prevents sidebar overflow; 50 is enough to explore |
| Bot paths | Render by default, toggleable | Cleaner human-only view | Shows full match picture; toggle handles preference |

---

## What I'd Do Differently With More Time

1. **DuckDB for data layer** — query parquet files directly without loading into memory; would handle 10x more data efficiently
2. **Animated playback** — a Play button that auto-increments the timeline slider using Streamlit's `st.session_state` and a loop
3. **Player drill-down** — click a player dot to see their full match stats (K/D, loot count, survival time)
4. **Map region labeling** — overlay named zones (like GrandRift's Mine Pit, Labour Quarters) on all maps for faster Level Designer orientation
5. **Cross-map comparison** — side-by-side heatmaps for the same metric across different maps

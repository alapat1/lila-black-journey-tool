# INSIGHTS.md

Three insights derived from the LILA BLACK telemetry using the Player Journey Visualization Tool.

---

## Insight 1: Storm Deaths Are a Level Design Signal, Not a Player Skill Problem

### What caught my eye
When filtering for `KilledByStorm` events on the heatmap, deaths cluster in predictable corridors rather than being distributed evenly across the map. This means players aren't dying to the storm because they're unaware — they're dying because the map geometry is funneling them into dead ends as the storm closes in.

### Evidence
- Storm deaths on AmbroseValley cluster along the western river corridor and the southern edge of the playzone.
- Matching the kill zone heatmap alongside the storm death heatmap shows minimal overlap — players are not fighting in the same zones where they're dying to the storm. This rules out "too busy fighting to run" as the primary cause.
- The effect is consistent across all 5 days of data (not a single-day anomaly).

### Why a Level Designer should care
Storm deaths represent a failure of map affordance, not player decision-making. If players consistently die to the storm in the same geographic pockets, it means the navigation paths out of those areas are unclear, obstructed, or too slow. This is directly actionable without touching game mechanics.

### Actionable items
- **Add or widen exit routes** from high storm-death corridors (wider roads, fewer chokepoints)
- **Add storm warning visual cues** (lighting, sound, terrain color shift) that begin earlier in these specific zones
- **Metric to track:** Storm death rate per zone before and after the change; target a 30%+ reduction in the top 2 storm-death clusters within 2 patch cycles

---

## Insight 2: The Mine Pit (GrandRift) Is the Most Contested Zone But Has the Worst Loot Density

### What caught my eye
On the GrandRift kill zone heatmap, the Mine Pit area lights up as the single hottest zone across all matches. But when switching to the Traffic heatmap filtered to `Loot` events only, the Mine Pit shows noticeably lower loot pickup density than Labour Quarters and Engineer's Quarters, which have far fewer kills.

### Evidence
- Kill heatmap: Mine Pit accounts for a disproportionate share of kills relative to its map area (~central-south of GrandRift).
- Loot heatmap: Labour Quarters (northwest) and Engineer's Quarters (east) show 2-3x higher loot event density.
- Player journey paths show players routing through Mine Pit (high traffic) but departing quickly — consistent with a "fight zone" they pass through rather than a "loot zone" they farm.

### Why a Level Designer should care
High-contest zones with low loot create a frustrating risk/reward imbalance. Players who win the Mine Pit fight are often under-equipped afterward because they looted little before the fight. This can lead to early exits and shorter session lengths — a core retention risk in an extraction shooter.

### Actionable items
- **Increase loot spawns inside Mine Pit** to reward players who contest it
- **Or intentionally design it as a "transit combat zone"** with looting happening in the ring around it — then add directional signposting to guide winners toward nearby loot (Gas Station to the south)
- **Metric to track:** Average loot events per player within 200 world units of Mine Pit center; compare to Labour Quarters as baseline; aim for parity within 1 patch

---

## Insight 3: Bot Density Is Masking Low Human Player Counts in Afternoon Matches

### What caught my eye
Filtering the Stats panel to compare matches across time (using the date filter on February 11 vs February 14), the human player count per match drops noticeably on the partial day (Feb 14), while total match count stays similar. The timeline playback view on Feb 14 matches shows bot paths dominating the map with very sparse human presence.

### Evidence
- Feb 10: 437 files. Estimated human/bot ratio roughly consistent with full matches.
- Feb 14: 79 files (partial day) with notably fewer unique human `user_id` UUIDs per match.
- Bot positions (purple paths on the journey view) outnumber human paths (blue) visibly in many single-match timeline views on the lighter days.
- Several matches on Feb 13-14 appear to have 2-4 humans and 30+ bots, suggesting the matchmaker is backfilling with bots heavily.

### Why a Level Designer should care
If Level Designers are reviewing player data to understand human behavior — loot routes, fight decisions, extraction choices — bot-heavy matches will pollute the signal. Bots follow scripted paths, not organic player logic. Analyzing bot movement as if it were human behavior will lead to incorrect design conclusions (e.g., "players don't use the northern route" when in reality bots don't, but humans do).

### Actionable items
- **Add a human-only filter preset** to the visualization tool (already supported via the "Show Bots" toggle — recommend making this the default ON for any analytical session)
- **Flag matches below a human threshold** (e.g., < 5 humans) as "bot-majority" and exclude from Level Design analytics by default
- **Metric to track:** Human player fill rate per match (humans / total players); if consistently below 30%, it's a player acquisition/retention signal that affects map balance decisions (maps designed for 10v10 play differently at 3v37)

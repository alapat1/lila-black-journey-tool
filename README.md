# LILA BLACK — Player Journey Visualization Tool

Built for the LILA Games Level Design team to stop staring at raw telemetry spreadsheets and actually *see* what's happening on their maps.

🔗 **[Open the tool here](https://lila-black-journey-tool-harsh11.streamlit.app/)**

---

## What is this?

LILA BLACK is an extraction shooter with 3 maps, hundreds of matches, and thousands of player events every day. The Level Design team had all this data sitting in parquet files but no way to make sense of it visually — where are players dying? Which zones are getting ignored? Are players actually moving the way the map was designed for?

This tool answers those questions. Drop in the telemetry data, pick a map and a match, and you can see exactly what happened — player paths drawn on the minimap, kill and death markers, heatmaps of contested zones, and a timeline scrubber to watch a match unfold second by second.

---

## Features

- **Player Journey Map** — renders every player's movement path on the correct minimap, with world coordinates properly converted to pixel positions
- **Human vs Bot** — blue paths are real players, purple are bots. Toggle bots on/off depending on what you're analyzing
- **Event Markers** — kills, deaths, loot pickups, and storm deaths all show up as distinct icons you can filter
- **Heatmaps** — overlay kill zones, death zones, or general traffic density on the map
- **Timeline Playback** — pick any match and scrub through it second by second to watch it unfold
- **Stats Panel** — event breakdowns, human/bot ratios, activity by day, top matches
- **Filters** — slice by map, date, and individual match ID

---

## Running it locally

You'll need Python 3.9+ installed.

```bash
# Clone the repo
git clone https://github.com/alapat1/lila-black-journey-tool.git
cd lila-black-journey-tool

# Install dependencies
pip install -r requirements.txt

# Run
python -m streamlit run app.py
```

Your folder structure needs to look like this:

```
lila-black-journey-tool/
├── app.py
├── requirements.txt
├── player_data/
│   ├── February_10/
│   ├── February_11/
│   ├── February_12/
│   ├── February_13/
│   └── February_14/
└── minimaps/
    ├── AmbroseValley_Minimap.png
    ├── GrandRift_Minimap.png
    └── Lockdown_Minimap.jpg
```

No environment variables needed.

---

## Tech stack

- **Streamlit** — the whole app is one Python file, which made iteration really fast
- **Plotly** — handles all the interactive map rendering, heatmaps, and charts
- **PyArrow + Pandas** — reads the parquet files and handles all data wrangling
- **SciPy** — gaussian smoothing for the heatmap overlays
- **Pillow** — loads and resizes the minimap images

See `ARCHITECTURE.md` for the full breakdown of decisions and tradeoffs.

---

## Docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — tech stack choices, data flow, coordinate mapping approach, tradeoffs
- [`INSIGHTS.md`](INSIGHTS.md) — 3 data-backed insights about player behavior discovered using this tool

---

*Built by Harshit as part of the LILA Games APM Written Test*

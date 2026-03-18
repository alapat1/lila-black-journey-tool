# LILA BLACK — Player Journey Visualization Tool

A web-based tool for LILA Games' Level Design team to explore player behavior across all 3 maps in LILA BLACK.

![LILA BLACK Tool](minimaps/AmbroseValley_Minimap.png)

## Live Demo

🔗 **[Open Tool →](YOUR_DEPLOYED_URL_HERE)**  
*(Replace with your Streamlit Cloud URL after deployment)*

---

## Features

| Feature | Description |
|---------|-------------|
| 🗺 Player Journeys | Render full player paths on the correct minimap with world→pixel coordinate mapping |
| 👤 Human vs Bot | Visually distinguish human players (blue) from bots (purple) |
| 📍 Event Markers | Kill, Death, Loot, Storm Death events shown as distinct symbols |
| 🔍 Filters | Filter by map, date, and individual match |
| ⏱ Timeline Playback | Scrub through a match second-by-second to watch it unfold |
| 🔥 Heatmaps | Kill zones, death zones, and player traffic overlays |
| 📊 Stats Panel | Event distribution, human/bot breakdown, top matches |

---

## Running Locally

### Requirements
- Python 3.9+
- pip

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/lila-journey-tool.git
cd lila-journey-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place data files
# Your folder structure should look like:
# lila-journey-tool/
# ├── app.py
# ├── requirements.txt
# ├── player_data/
# │   ├── February_10/
# │   ├── February_11/
# │   ├── February_12/
# │   ├── February_13/
# │   └── February_14/
# └── minimaps/
#     ├── AmbroseValley_Minimap.png
#     ├── GrandRift_Minimap.png
#     └── Lockdown_Minimap.jpg

# 4. Run
streamlit run app.py
```

The tool will open at `http://localhost:8501`.

### Environment Variables
No environment variables required.

---

## Deploying to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Deploy**

> **Note:** Streamlit Cloud has a 1GB file size limit. If your `player_data/` folder is large, consider hosting data separately (e.g., on Google Drive or S3) and adapting the loader.

---

## Tech Stack

- **Frontend/App:** [Streamlit](https://streamlit.io) — Python-native web app framework
- **Visualization:** [Plotly](https://plotly.com/python/) — interactive maps and charts
- **Data:** [PyArrow](https://arrow.apache.org/docs/python/) + [Pandas](https://pandas.pydata.org/) — parquet reading
- **Heatmaps:** [SciPy](https://scipy.org/) gaussian_filter for smooth density overlays
- **Images:** [Pillow](https://pillow.readthedocs.io/) — minimap loading

See `ARCHITECTURE.md` for full design decisions.

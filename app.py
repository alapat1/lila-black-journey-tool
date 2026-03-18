import streamlit as st
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import os
import glob
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LILA BLACK — Player Journey Tool",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (dark game aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    background-color: #0a0c10 !important;
    color: #c8d6e5 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stApp { background: #0a0c10 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e2d3d !important;
}

/* Header */
.main-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #00d4ff;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 20px rgba(0,212,255,0.4);
}
.sub-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #4a6080;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Metric cards */
.metric-card {
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-top: 2px solid #00d4ff;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #4a6080;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #00d4ff;
}

/* Section labels */
.section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #4a6080;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem 0;
}

/* Selectboxes, sliders */
.stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.65rem !important;
    color: #4a6080 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid #00d4ff !important;
    color: #00d4ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117 !important;
    border-bottom: 1px solid #1e2d3d !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #4a6080 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
}

div[data-testid="stPlotlyChart"] {
    border: 1px solid #1e2d3d;
    border-radius: 4px;
}

/* expander */
.streamlit-expanderHeader {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #4a6080 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473, "img": "minimaps/AmbroseValley_Minimap.png"},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290, "img": "minimaps/GrandRift_Minimap.png"},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500, "img": "minimaps/Lockdown_Minimap.jpg"},
}

EVENT_COLORS = {
    "Position":      "#3a86ff",
    "BotPosition":   "#8338ec",
    "Kill":          "#ff006e",
    "Killed":        "#fb5607",
    "BotKill":       "#ffbe0b",
    "BotKilled":     "#ff9f1c",
    "KilledByStorm": "#06d6a0",
    "Loot":          "#ffd166",
}

EVENT_SYMBOLS = {
    "Position":      "circle",
    "BotPosition":   "square",
    "Kill":          "x",
    "Killed":        "x-open",
    "BotKill":       "diamond",
    "BotKilled":     "diamond-open",
    "KilledByStorm": "star",
    "Loot":          "triangle-up",
}

EVENT_SIZES = {
    "Position": 3, "BotPosition": 3,
    "Kill": 12, "Killed": 12,
    "BotKill": 9, "BotKilled": 9,
    "KilledByStorm": 14, "Loot": 8,
}

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def world_to_pixel(x, z, map_name, img_size=1024):
    cfg = MAP_CONFIG[map_name]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * img_size
    py = (1 - v) * img_size
    return px, py

def is_bot(user_id):
    try:
        float(str(user_id))
        return True
    except:
        return False

@st.cache_data(show_spinner=False)
def load_all_data(data_root):
    frames = []
    days = sorted([d for d in os.listdir(data_root) if os.path.isdir(os.path.join(data_root, d))])
    for day in days:
        day_path = os.path.join(data_root, day)
        files = os.listdir(day_path)
        for f in files:
            fp = os.path.join(day_path, f)
            try:
                df = pq.read_table(fp).to_pandas()
                df['event'] = df['event'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else str(x)
                )
                df['day'] = day
                # Extract user_id and match_id from filename if missing
                parts = f.split('_')
                if 'user_id' not in df.columns or df['user_id'].isna().all():
                    df['user_id'] = parts[0] if parts else 'unknown'
                if 'match_id' not in df.columns or df['match_id'].isna().all():
                    df['match_id'] = '_'.join(parts[1:]).replace('.nakama-0','') if len(parts)>1 else 'unknown'
                df['is_bot'] = df['user_id'].apply(lambda u: is_bot(str(u)))
                frames.append(df)
            except Exception:
                continue
    if not frames:
        return pd.DataFrame()
    result = pd.concat(frames, ignore_index=True)
    # Decode match_id suffix
    if 'match_id' in result.columns:
        result['match_id'] = result['match_id'].astype(str).str.replace('.nakama-0','', regex=False)
    result['px'], result['py'] = zip(*result.apply(
        lambda r: world_to_pixel(r['x'], r['z'], r['map_id']) if r['map_id'] in MAP_CONFIG else (None, None), axis=1
    ))
    result = result.dropna(subset=['px','py'])
    return result

def make_heatmap_figure(df, map_name, heatmap_type, img_size=1024):
    cfg = MAP_CONFIG[map_name]
    img_path = cfg["img"]
    try:
        img = Image.open(img_path).convert("RGBA").resize((img_size, img_size))
    except:
        img = Image.new("RGBA", (img_size, img_size), (20,20,30,255))

    if heatmap_type == "Kill Zones":
        sub = df[df['event'].isin(['Kill','BotKill'])]
        colorscale = [[0,'rgba(255,0,110,0)'],[0.4,'rgba(255,0,110,0.5)'],[1,'rgba(255,0,110,0.95)']]
        title_str = "Kill Zones"
    elif heatmap_type == "Death Zones":
        sub = df[df['event'].isin(['Killed','BotKilled','KilledByStorm'])]
        colorscale = [[0,'rgba(6,214,160,0)'],[0.4,'rgba(6,214,160,0.5)'],[1,'rgba(6,214,160,0.95)']]
        title_str = "Death Zones"
    else:  # Traffic
        sub = df[df['event'].isin(['Position','BotPosition'])]
        colorscale = [[0,'rgba(58,134,255,0)'],[0.4,'rgba(58,134,255,0.5)'],[1,'rgba(58,134,255,0.95)']]
        title_str = "Traffic Heatmap"

    heatmap_arr = np.zeros((img_size, img_size))
    if len(sub) > 0:
        xs = sub['px'].clip(0, img_size-1).astype(int)
        ys = sub['py'].clip(0, img_size-1).astype(int)
        for xi, yi in zip(xs, ys):
            heatmap_arr[yi, xi] += 1
        heatmap_arr = gaussian_filter(heatmap_arr, sigma=20)
        if heatmap_arr.max() > 0:
            heatmap_arr = heatmap_arr / heatmap_arr.max()

    fig = go.Figure()
    fig.add_layout_image(
        dict(source=img, x=0, y=0, xref="x", yref="y",
             sizex=img_size, sizey=img_size, sizing="stretch",
             xanchor="left", yanchor="bottom", layer="below")
    )
    fig.add_trace(go.Heatmap(
        z=heatmap_arr,
        colorscale=colorscale,
        showscale=False,
        opacity=0.75,
        x0=0, dx=1, y0=0, dy=1,
    ))
    fig.update_layout(
        width=700, height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#0a0c10',
        plot_bgcolor='#0a0c10',
        title=dict(text=title_str, font=dict(color='#00d4ff', family='Rajdhani', size=16)),
        xaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x'),
    )
    return fig

def make_journey_figure(df, map_name, show_bots, selected_events, img_size=1024):
    cfg = MAP_CONFIG[map_name]
    img_path = cfg["img"]
    try:
        img = Image.open(img_path).convert("RGBA").resize((img_size, img_size))
    except:
        img = Image.new("RGBA", (img_size, img_size), (20,20,30,255))

    plot_df = df.copy()
    if not show_bots:
        plot_df = plot_df[~plot_df['is_bot']]
    if selected_events:
        plot_df = plot_df[plot_df['event'].isin(selected_events)]

    fig = go.Figure()
    fig.add_layout_image(
        dict(source=img, x=0, y=0, xref="x", yref="y",
             sizex=img_size, sizey=img_size, sizing="stretch",
             xanchor="left", yanchor="bottom", layer="below")
    )

    # Draw movement paths per player (lines)
    pos_df = plot_df[plot_df['event'].isin(['Position','BotPosition'])].copy()
    if len(pos_df) > 0:
        for uid, grp in pos_df.groupby('user_id'):
            grp = grp.sort_values('ts')
            color = '#3a86ff' if not grp['is_bot'].iloc[0] else '#8338ec'
            fig.add_trace(go.Scatter(
                x=grp['px'], y=grp['py'],
                mode='lines',
                line=dict(color=color, width=1),
                opacity=0.25,
                name=f"{'Bot' if grp['is_bot'].iloc[0] else 'Human'} path",
                showlegend=False,
                hoverinfo='skip',
            ))

    # Draw event markers
    for evt in plot_df['event'].unique():
        if evt in ['Position', 'BotPosition']:
            continue
        sub = plot_df[plot_df['event'] == evt]
        if len(sub) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=sub['px'], y=sub['py'],
            mode='markers',
            name=evt,
            marker=dict(
                symbol=EVENT_SYMBOLS.get(evt, 'circle'),
                size=EVENT_SIZES.get(evt, 8),
                color=EVENT_COLORS.get(evt, '#ffffff'),
                line=dict(width=1, color='#0a0c10'),
            ),
            customdata=sub[['user_id','match_id','ts']].values,
            hovertemplate=(
                f"<b>{evt}</b><br>"
                "Player: %{customdata[0]}<br>"
                "Match: %{customdata[1]}<br>"
                "Time: %{customdata[2]}<extra></extra>"
            ),
        ))

    fig.update_layout(
        width=750, height=750,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='#0a0c10',
        plot_bgcolor='#0a0c10',
        legend=dict(
            bgcolor='rgba(13,17,23,0.9)',
            bordercolor='#1e2d3d',
            borderwidth=1,
            font=dict(color='#c8d6e5', family='Rajdhani', size=11),
        ),
        xaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x'),
    )
    return fig

def make_timeline_figure(match_df, map_name, time_window, img_size=1024):
    cfg = MAP_CONFIG[map_name]
    img_path = cfg["img"]
    try:
        img = Image.open(img_path).convert("RGBA").resize((img_size, img_size))
    except:
        img = Image.new("RGBA", (img_size, img_size), (20,20,30,255))

    t_min = match_df['ts_seconds'].min()
    t_max = match_df['ts_seconds'].max()
    window_start = time_window
    window_end = time_window + 30  # 30 second window

    window_df = match_df[(match_df['ts_seconds'] >= window_start) & (match_df['ts_seconds'] <= window_end)]

    fig = go.Figure()
    fig.add_layout_image(
        dict(source=img, x=0, y=0, xref="x", yref="y",
             sizex=img_size, sizey=img_size, sizing="stretch",
             xanchor="left", yanchor="bottom", layer="below")
    )

    # Paths up to this point (faded)
    past_df = match_df[match_df['ts_seconds'] <= window_end]
    for uid, grp in past_df[past_df['event'].isin(['Position','BotPosition'])].groupby('user_id'):
        grp = grp.sort_values('ts_seconds')
        color = '#3a86ff' if not grp['is_bot'].iloc[0] else '#8338ec'
        fig.add_trace(go.Scatter(
            x=grp['px'], y=grp['py'],
            mode='lines',
            line=dict(color=color, width=1),
            opacity=0.15,
            showlegend=False, hoverinfo='skip'
        ))

    # Current positions (bright dots)
    current = window_df[window_df['event'].isin(['Position','BotPosition'])]
    if len(current) > 0:
        latest = current.sort_values('ts_seconds').groupby('user_id').last().reset_index()
        humans = latest[~latest['is_bot']]
        bots = latest[latest['is_bot']]
        if len(humans):
            fig.add_trace(go.Scatter(
                x=humans['px'], y=humans['py'], mode='markers',
                name='Human', marker=dict(size=8, color='#3a86ff', symbol='circle',
                line=dict(width=2, color='#00d4ff')),
            ))
        if len(bots):
            fig.add_trace(go.Scatter(
                x=bots['px'], y=bots['py'], mode='markers',
                name='Bot', marker=dict(size=6, color='#8338ec', symbol='square',
                line=dict(width=1, color='#a855f7')),
            ))

    # Events in this window
    evts = window_df[~window_df['event'].isin(['Position','BotPosition'])]
    for evt in evts['event'].unique():
        sub = evts[evts['event']==evt]
        fig.add_trace(go.Scatter(
            x=sub['px'], y=sub['py'], mode='markers',
            name=evt,
            marker=dict(symbol=EVENT_SYMBOLS.get(evt,'circle'),
                       size=EVENT_SIZES.get(evt,8)+4,
                       color=EVENT_COLORS.get(evt,'#fff'),
                       line=dict(width=2, color='#fff')),
        ))

    fig.update_layout(
        width=750, height=750,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='#0a0c10',
        plot_bgcolor='#0a0c10',
        legend=dict(bgcolor='rgba(13,17,23,0.9)', bordercolor='#1e2d3d', borderwidth=1,
                   font=dict(color='#c8d6e5', family='Rajdhani', size=11)),
        xaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0,img_size], showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x'),
        title=dict(text=f"T+{int(window_start)}s — T+{int(window_end)}s",
                  font=dict(color='#00d4ff', family='Share Tech Mono', size=13))
    )
    return fig

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-header">LILA BLACK</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Player Journey Visualization</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Data Source</div>', unsafe_allow_html=True)
    data_root = st.text_input("player_data folder path", value="player_data", label_visibility="collapsed")

    if not os.path.exists(data_root):
        st.error(f"Folder not found: `{data_root}`\n\nPlease make sure `player_data/` is in the same directory as `app.py`.")
        st.stop()

    with st.spinner("Loading data..."):
        df_all = load_all_data(data_root)

    if df_all.empty:
        st.error("No data could be loaded. Check folder structure.")
        st.stop()

    st.success(f"{len(df_all):,} events loaded")

    st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)

    # Map filter
    available_maps = sorted(df_all['map_id'].unique())
    selected_map = st.selectbox("MAP", available_maps)

    df_map = df_all[df_all['map_id'] == selected_map]

    # Day filter
    available_days = sorted(df_map['day'].unique())
    selected_days = st.multiselect("DATE", available_days, default=available_days[:1])

    if selected_days:
        df_day = df_map[df_map['day'].isin(selected_days)]
    else:
        df_day = df_map

    # Match filter
    available_matches = sorted(df_day['match_id'].unique())
    match_options = ["All Matches"] + list(available_matches[:50])
    selected_match_label = st.selectbox("MATCH", match_options)

    if selected_match_label == "All Matches":
        df_filtered = df_day
    else:
        df_filtered = df_day[df_day['match_id'] == selected_match_label]

    st.markdown('<div class="section-label">Display</div>', unsafe_allow_html=True)
    show_bots = st.checkbox("Show Bots", value=True)

    all_events = list(EVENT_COLORS.keys())
    selected_events = st.multiselect(
        "EVENT TYPES",
        all_events,
        default=all_events
    )

# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────
# Stats row
col1, col2, col3, col4, col5 = st.columns(5)
n_matches = df_filtered['match_id'].nunique()
n_players = df_filtered[~df_filtered['is_bot']]['user_id'].nunique()
n_bots = df_filtered[df_filtered['is_bot']]['user_id'].nunique()
n_kills = len(df_filtered[df_filtered['event'].isin(['Kill','BotKill'])])
n_storm = len(df_filtered[df_filtered['event']=='KilledByStorm'])

for col, label, val in zip(
    [col1, col2, col3, col4, col5],
    ["MATCHES", "HUMAN PLAYERS", "BOTS", "KILLS", "STORM DEATHS"],
    [n_matches, n_players, n_bots, n_kills, n_storm]
):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val:,}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_journey, tab_heatmap, tab_timeline, tab_stats = st.tabs([
    "🗺  PLAYER JOURNEYS", "🔥  HEATMAPS", "⏱  TIMELINE / PLAYBACK", "📊  STATS"
])

# ──── TAB 1: PLAYER JOURNEYS ────
with tab_journey:
    col_map, col_ctrl = st.columns([3, 1])
    with col_ctrl:
        st.markdown('<div class="section-label">Legend</div>', unsafe_allow_html=True)
        for evt, color in EVENT_COLORS.items():
            if evt in selected_events:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
                    f'<div style="width:12px;height:12px;background:{color};border-radius:50%;flex-shrink:0;"></div>'
                    f'<span style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#4a6080;">{evt}</span>'
                    f'</div>', unsafe_allow_html=True
                )
        st.markdown('<div class="section-label" style="margin-top:1rem;">Info</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4a6080;line-height:1.8;">
        Events: {len(df_filtered):,}<br>
        Humans: {'shown' if not show_bots or True else 'hidden'}<br>
        Bots: {'shown' if show_bots else 'hidden'}
        </div>""", unsafe_allow_html=True)

    with col_map:
        with st.spinner("Rendering map..."):
            fig = make_journey_figure(df_filtered, selected_map, show_bots, selected_events)
        st.plotly_chart(fig, use_container_width=False)

# ──── TAB 2: HEATMAPS ────
with tab_heatmap:
    col_hm, col_hctrl = st.columns([3, 1])
    with col_hctrl:
        st.markdown('<div class="section-label">Heatmap Type</div>', unsafe_allow_html=True)
        heatmap_type = st.radio(
            "type", ["Kill Zones", "Death Zones", "Traffic"],
            label_visibility="collapsed"
        )
        st.markdown('<div class="section-label" style="margin-top:1rem;">About</div>', unsafe_allow_html=True)
        descriptions = {
            "Kill Zones": "Where kills happen most. Red hotspots = contested areas.",
            "Death Zones": "Where players die most. Includes storm deaths.",
            "Traffic": "Where players spend the most time moving.",
        }
        st.markdown(f'<div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4a6080;line-height:1.8;">{descriptions[heatmap_type]}</div>', unsafe_allow_html=True)

        # Stats for heatmap type
        if heatmap_type == "Kill Zones":
            count = len(df_filtered[df_filtered['event'].isin(['Kill','BotKill'])])
            label = "Total Kills"
        elif heatmap_type == "Death Zones":
            count = len(df_filtered[df_filtered['event'].isin(['Killed','BotKilled','KilledByStorm'])])
            label = "Total Deaths"
        else:
            count = len(df_filtered[df_filtered['event'].isin(['Position','BotPosition'])])
            label = "Position Samples"
        st.markdown(f"""
        <div class="metric-card" style="margin-top:1rem;">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{count:,}</div>
        </div>""", unsafe_allow_html=True)

    with col_hm:
        with st.spinner("Building heatmap..."):
            hfig = make_heatmap_figure(df_filtered, selected_map, heatmap_type)
        st.plotly_chart(hfig, use_container_width=False)

# ──── TAB 3: TIMELINE ────
with tab_timeline:
    st.markdown('<div class="section-label">Select a Single Match to Enable Playback</div>', unsafe_allow_html=True)

    if selected_match_label == "All Matches":
        st.info("Select a specific match from the sidebar to use the timeline playback feature.")
    else:
        match_df = df_filtered.copy()
        match_df['ts_seconds'] = (match_df['ts'] - match_df['ts'].min()).dt.total_seconds()
        t_min = int(match_df['ts_seconds'].min())
        t_max = int(match_df['ts_seconds'].max())

        col_tl, col_tctrl = st.columns([3, 1])
        with col_tctrl:
            st.markdown('<div class="section-label">Playback</div>', unsafe_allow_html=True)
            time_val = st.slider(
                "Match Time (seconds)",
                min_value=t_min, max_value=max(t_min+1, t_max-30),
                value=t_min, step=5,
                label_visibility="visible"
            )
            st.markdown('<div class="section-label" style="margin-top:1rem;">Match Info</div>', unsafe_allow_html=True)
            duration = t_max - t_min
            n_humans_match = match_df[~match_df['is_bot']]['user_id'].nunique()
            n_bots_match = match_df[match_df['is_bot']]['user_id'].nunique()
            st.markdown(f"""
            <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4a6080;line-height:2.0;">
            Duration: {int(duration)}s<br>
            Humans: {n_humans_match}<br>
            Bots: {n_bots_match}<br>
            Events: {len(match_df):,}
            </div>""", unsafe_allow_html=True)

        with col_tl:
            with st.spinner("Rendering timeline..."):
                tfig = make_timeline_figure(match_df, selected_map, time_val)
            st.plotly_chart(tfig, use_container_width=False)

# ──── TAB 4: STATS ────
with tab_stats:
    scol1, scol2 = st.columns(2)

    with scol1:
        st.markdown('<div class="section-label">Event Distribution</div>', unsafe_allow_html=True)
        evt_counts = df_filtered['event'].value_counts().reset_index()
        evt_counts.columns = ['event', 'count']
        evt_counts['color'] = evt_counts['event'].map(EVENT_COLORS).fillna('#ffffff')

        bar_fig = go.Figure(go.Bar(
            x=evt_counts['count'], y=evt_counts['event'],
            orientation='h',
            marker_color=evt_counts['color'],
            text=evt_counts['count'].apply(lambda x: f"{x:,}"),
            textposition='outside',
            textfont=dict(color='#c8d6e5', family='Share Tech Mono', size=10),
        ))
        bar_fig.update_layout(
            paper_bgcolor='#0a0c10', plot_bgcolor='#0a0c10',
            margin=dict(l=10, r=60, t=10, b=10),
            height=320,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, color='#4a6080'),
            yaxis=dict(showgrid=False, zeroline=False, color='#c8d6e5',
                      tickfont=dict(family='Share Tech Mono', size=10)),
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        st.markdown('<div class="section-label">Human vs Bot Breakdown</div>', unsafe_allow_html=True)
        hb_counts = df_filtered['is_bot'].value_counts()
        pie_fig = go.Figure(go.Pie(
            labels=['Human', 'Bot'],
            values=[hb_counts.get(False, 0), hb_counts.get(True, 0)],
            marker_colors=['#3a86ff', '#8338ec'],
            textfont=dict(family='Rajdhani', size=14, color='#c8d6e5'),
            hole=0.5,
        ))
        pie_fig.update_layout(
            paper_bgcolor='#0a0c10', margin=dict(l=0,r=0,t=10,b=0), height=220,
            legend=dict(font=dict(color='#c8d6e5', family='Rajdhani'), bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with scol2:
        st.markdown('<div class="section-label">Activity by Day</div>', unsafe_allow_html=True)
        day_counts = df_filtered.groupby('day')['event'].count().reset_index()
        day_counts.columns = ['day', 'events']
        area_fig = go.Figure(go.Scatter(
            x=day_counts['day'], y=day_counts['events'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#00d4ff', width=2),
            fillcolor='rgba(0,212,255,0.1)',
            marker=dict(size=6, color='#00d4ff'),
        ))
        area_fig.update_layout(
            paper_bgcolor='#0a0c10', plot_bgcolor='#0a0c10',
            margin=dict(l=10, r=10, t=10, b=10), height=220,
            xaxis=dict(color='#4a6080', showgrid=False, zeroline=False,
                      tickfont=dict(family='Share Tech Mono', size=9)),
            yaxis=dict(color='#4a6080', showgrid=True, gridcolor='#1e2d3d', zeroline=False,
                      tickfont=dict(family='Share Tech Mono', size=9)),
        )
        st.plotly_chart(area_fig, use_container_width=True)

        st.markdown('<div class="section-label">Top Matches by Activity</div>', unsafe_allow_html=True)
        match_activity = df_filtered.groupby('match_id').agg(
            events=('event','count'),
            humans=('is_bot', lambda x: (~x).sum()),
            bots=('is_bot', 'sum'),
            kills=('event', lambda x: (x.isin(['Kill','BotKill'])).sum()),
        ).sort_values('events', ascending=False).head(8).reset_index()

        match_activity['match_short'] = match_activity['match_id'].str[:8] + '...'

        table_fig = go.Figure(go.Table(
            header=dict(
                values=['MATCH', 'EVENTS', 'HUMANS', 'BOTS', 'KILLS'],
                fill_color='#0d1117',
                font=dict(color='#00d4ff', family='Share Tech Mono', size=9),
                align='left',
                line_color='#1e2d3d',
            ),
            cells=dict(
                values=[
                    match_activity['match_short'],
                    match_activity['events'],
                    match_activity['humans'],
                    match_activity['bots'],
                    match_activity['kills'],
                ],
                fill_color='#0a0c10',
                font=dict(color='#c8d6e5', family='Share Tech Mono', size=9),
                align='left',
                line_color='#1e2d3d',
            )
        ))
        table_fig.update_layout(
            paper_bgcolor='#0a0c10', margin=dict(l=0,r=0,t=0,b=0), height=260,
        )
        st.plotly_chart(table_fig, use_container_width=True)

# Footer
st.markdown("""
<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #1e2d3d;
    font-family:Share Tech Mono,monospace;font-size:0.55rem;color:#2a3d54;
    text-align:center;letter-spacing:0.2em;text-transform:uppercase;">
LILA BLACK — Player Journey Visualization Tool — Built for LILA Games Level Design Team
</div>
""", unsafe_allow_html=True)

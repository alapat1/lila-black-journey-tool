Stack
Streamlit + Plotly + Pandas + SciPy
Streamlit because the whole app ends up being one Python file and deploys for free in minutes. No frontend code needed, which meant I could focus on getting the data right rather than wrestling with a React setup. Plotly handles all the interactive map rendering it supports image underlays natively, which is exactly what you need to overlay player paths on a minimap. Pandas + PyArrow for reading parquet, SciPy for smoothing the heatmaps.

Data flow
player_data/ folders
  → PyArrow reads each .nakama-0 file
  → decode event bytes, classify bots by user_id shape
  → convert world (x, z) coordinates to minimap pixels
  → cache everything in memory on first load
  → sidebar filters slice the dataframe
  → Plotly renders the result
The whole dataset loads once on startup and gets cached. Filters after that are instant.

Coordinate mapping
This was the trickiest part. The game uses 3D coordinates (x, y, z) but the minimap is 2D. Y is elevation, ignored. X and Z map to the minimap using each map's scale and origin values from the README:
u = (x - origin_x) / scale
v = (z - origin_z) / scale
pixel_x = u * 1024
pixel_y = (1 - v) * 1024   ← Y needs to be flipped
The flip on pixel_y is the key thing, minimap images have (0,0) at the top-left, but world Z increases upward. Without the flip everything appears mirrored vertically.

Assumptions
Numeric user_id means bot, UUID means human, straight from the README. I stripped the .nakama-0 suffix from match IDs since it's just a server tag. For the timeline I used relative time within each match rather than wall-clock time. February 14 being a partial day didn't need any special handling.

Tradeoffs
I loaded all files into memory at startup and cached them, makes filters instant but uses more RAM. For heatmaps I went with server-side numpy + gaussian blur instead of WebGL rendering, simpler to implement. The timeline is a scrub slider rather than an auto-play button, which works fine but isn't as smooth. I capped the match list in the sidebar at 50 to avoid it getting unwieldy.

What I'd do differently with more time
Use DuckDB to query parquet directly instead of loading everything into memory, would scale to much larger datasets. Add animated playback instead of just a scrub slider. Let you click a player dot to see their full match stats. Add named zone labels to all 3 maps so level designers can orient faster.

import math
from datetime import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Solar Tracker | Fuzzy Control", page_icon="☀️", layout="wide")

# ---------- Fuzzy-logic helpers (triangular membership functions) ----------
def tri(x, a, b, c):
    """Triangular membership degree in [0, 1]."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a) if b != a else 1.0
    return (c - x) / (c - b) if c != b else 1.0

def fuzzy_sun_position(hour):
    """
    Simple educational solar-position approximation for a daytime demo.
    Returns azimuth-like horizontal angle and elevation-like vertical angle.
    This is a simulation, not a location-specific astronomical calculation.
    """
    # Map 06:00..18:00 to -90..+90 degrees around solar noon.
    hour_angle = (hour - 12.0) * 15.0
    horizontal = max(-90.0, min(90.0, hour_angle))
    # Elevation peaks at noon; 0 at 06:00 and 18:00.
    elevation = max(0.0, 75.0 * math.sin(math.pi * (hour - 6.0) / 12.0))
    return horizontal, elevation

def fuzzy_correction(error):
    """
    Tiny Mamdani-style rule system.
    Input: normalized tracking error (-1..1).
    Output: correction (-10..10 degrees), centroid approximation by weighted consequents.
    """
    e = max(-1.0, min(1.0, error))
    neg = tri(e, -1.0, -1.0, 0.0) if e < 0 else 0.0
    zero = tri(e, -0.35, 0.0, 0.35)
    pos = tri(e, 0.0, 1.0, 1.0) if e > 0 else 0.0
    rules = [(neg, -10.0), (zero, 0.0), (pos, 10.0)]
    denom = sum(strength for strength, _ in rules)
    if denom == 0:
        return 0.0
    return sum(strength * output for strength, output in rules) / denom

def fuzzy_label(error):
    if error < -0.25:
        return "Negative / move left"
    if error > 0.25:
        return "Positive / move right"
    return "Near centre / hold"

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#10233f,#174b61); color: white; margin-bottom: 1rem;}
.hero h1 {margin:0; font-size:2rem;}
.hero p {margin:.4rem 0 0; color:#dbeafe;}
.small-note {font-size:.88rem; color: #64748b;}
div[data-testid="stMetric"] {background: rgba(128,128,128,.07); border: 1px solid rgba(128,128,128,.15); padding: 12px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>☀️ Solar Panel Tracker</h1>
  <p>Time-based dual-axis tracker simulation powered by fuzzy rules — no microcontroller or hardware required.</p>
</div>
""", unsafe_allow_html=True)

st.info("Demo mode: choose a time between 06:00 AM and 06:00 PM. The app estimates panel angles and fuzzy-controller output. It does not control a physical motor.")

# The only user-adjustable project parameter is time, constrained to 06:00–18:00.
selected_time = st.slider(
    "Select daytime (06:00 AM – 06:00 PM)",
    min_value=6.0, max_value=18.0, value=12.0, step=0.25,
    format="%.2f hours"
)
hour = float(selected_time)
hh = int(hour)
mm = int(round((hour - hh) * 60))
if mm == 60:
    hh, mm = hh + 1, 0
display_time = f"{hh % 12 or 12:02d}:{mm:02d} {'AM' if hh < 12 else 'PM'}"

horizontal, elevation = fuzzy_sun_position(hour)

# Approximate fuzzy tracking error from the sun's horizontal position.
# A second fuzzy axis is used to illustrate vertical positioning.
horizontal_error = max(-1.0, min(1.0, horizontal / 90.0))
vertical_error = max(-1.0, min(1.0, (45.0 - elevation) / 75.0))
horizontal_correction = fuzzy_correction(horizontal_error)
vertical_correction = fuzzy_correction(vertical_error)

# Panel angles are clamped to practical demonstration ranges.
azimuth_angle = max(0.0, min(180.0, 90.0 + horizontal))
tilt_angle = max(0.0, min(90.0, elevation))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Selected time", display_time)
c2.metric("Horizontal / azimuth", f"{azimuth_angle:.1f}°")
c3.metric("Vertical / tilt", f"{tilt_angle:.1f}°")
c4.metric("Fuzzy status", "Tracking" if 6.1 < hour < 17.9 else "Low sun")

st.divider()
left, right = st.columns([1.15, 1])

with left:
    st.subheader("Panel orientation")
    fig = go.Figure()
    # Side view: ground and panel represented as a line based on tilt.
    x0, y0 = 0, 0
    length = 1.0
    rad = math.radians(tilt_angle)
    x1, y1 = length * math.cos(rad), length * math.sin(rad)
    fig.add_trace(go.Scatter(x=[-1.2, 1.2], y=[0, 0], mode="lines",
                             line=dict(width=4, color="#64748b"), name="Ground"))
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines+markers",
                             line=dict(width=12, color="#f59e0b"), marker=dict(size=8),
                             name="Solar panel"))
    fig.add_trace(go.Scatter(x=[x1, x1 + 0.25 * math.cos(rad + math.pi/2)],
                             y=[y1, y1 + 0.25 * math.sin(rad + math.pi/2)],
                             mode="lines", line=dict(width=3, color="#38bdf8"),
                             name="Panel normal"))
    fig.update_layout(height=330, margin=dict(l=10,r=10,t=20,b=10),
                      xaxis=dict(visible=False, range=[-1.3, 1.3]),
                      yaxis=dict(visible=False, range=[-0.2, 1.25], scaleanchor="x"),
                      legend=dict(orientation="h", y=-0.12),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Illustrative side-view visualization. Actual sun angles depend on date and geographic location.")

with right:
    st.subheader("Fuzzy controller output")
    st.metric("Horizontal correction", f"{horizontal_correction:+.1f}°")
    st.write(f"**Rule result:** {fuzzy_label(horizontal_error)}")
    st.progress(min(1.0, abs(horizontal_error)))
    st.caption(f"Normalized horizontal error: {horizontal_error:+.2f}")

    st.metric("Vertical correction", f"{vertical_correction:+.1f}°")
    st.write(f"**Rule result:** {fuzzy_label(vertical_error)}")
    st.progress(min(1.0, abs(vertical_error)))
    st.caption(f"Normalized vertical error: {vertical_error:+.2f}")

st.subheader("Fuzzy rules used")
rules = pd.DataFrame([
    {"Input membership": "Negative", "Condition": "Tracking error is negative", "Output": "Move in negative direction (−10°)"},
    {"Input membership": "Zero", "Condition": "Tracking error is near zero", "Output": "Hold position (0°)"},
    {"Input membership": "Positive", "Condition": "Tracking error is positive", "Output": "Move in positive direction (+10°)"},
])
st.dataframe(rules, hide_index=True, use_container_width=True)

st.subheader("Daytime tracking profile")
hours = [6 + i * 0.25 for i in range(49)]
rows = []
for h in hours:
    az, el = fuzzy_sun_position(h)
    rows.append({"Time": f"{int(h):02d}:{int(round((h-int(h))*60)):02d}",
                 "Azimuth angle (°)": max(0.0, min(180.0, 90.0 + az)),
                 "Tilt angle (°)": max(0.0, min(90.0, el))})
profile = pd.DataFrame(rows)
chart = go.Figure()
chart.add_trace(go.Scatter(x=profile["Time"], y=profile["Azimuth angle (°)"],
                           name="Azimuth", mode="lines", line=dict(width=3)))
chart.add_trace(go.Scatter(x=profile["Time"], y=profile["Tilt angle (°)"],
                           name="Tilt", mode="lines", line=dict(width=3)))
selected_hour = st.slider(
    "Select Time",
    min_value=6,
    max_value=18,
    value=12,
    step=1
)

selected_time_label = (
    f"{selected_hour % 12 or 12}:00 "
    f"{'AM' if selected_hour < 12 else 'PM'}"
)
chart.update_layout(height=330, xaxis_title="Time (06:00–18:00)", yaxis_title="Angle (degrees)",
                    margin=dict(l=10,r=10,t=25,b=10), legend=dict(orientation="h", y=1.12),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(chart, use_container_width=True)

with st.expander("How the fuzzy logic works"):
    st.markdown("""
    1. The selected time is converted into a **simulated horizontal position** and **solar elevation**.
    2. Each axis gets a normalized tracking error between **−1 and +1**.
    3. Triangular membership functions classify the error as **Negative**, **Zero**, or **Positive**.
    4. Three fuzzy rules produce a correction: **−10°**, **0°**, or **+10°**. The displayed output is a weighted average of rule consequents.
    5. Angles are limited to the daytime demonstration range of **06:00 AM to 06:00 PM**.

    This is a student-project simulation, not a calibrated solar ephemeris or a physical controller. For real tracking, use calibrated LDR readings (or a verified solar-position algorithm), motor limits, and suitable electrical/mechanical safety controls.
    """)

st.caption("Solar Tracker Project • Streamlit + Python + fuzzy-rule simulation")

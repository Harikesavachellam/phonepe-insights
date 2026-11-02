"""Plotly charts and explicit matching between data names and map names."""

import json
from pathlib import Path
import plotly.express as px

ASSETS = Path(__file__).resolve().parent / "assets"
COLORS = ["#a78bfa", "#2dd4bf", "#fbbf24", "#f472b6", "#60a5fa"]
LABELS = {"transaction_count": "Transactions", "amount": "Value (INR)",
          "registered_users": "Registered users", "app_opens": "App opens"}
STATE_ALIASES = {
    "andaman-&-nicobar-islands": "andaman-and-nicobar",
    "dadra-&-nagar-haveli-&-daman-&-diu": "dadra-and-nagar-haveli-and-daman-and-diu",
    "jammu-&-kashmir": "jammu-and-kashmir",
    "andaman-and-nicobar-islands": "andaman-and-nicobar",
}


def pretty_name(name):
    return str(name).replace("-", " ").title()


def normalize_state(name):
    name = name.lower().replace(" & ", " and ").replace(" ", "-")
    return STATE_ALIASES.get(name, name)


def normalize_district(name):
    return str(name).lower().replace(" district", "").replace(" ", "").replace("-", "")


def style_chart(figure, height=360):
    figure.update_layout(template="plotly_dark", height=height,
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                         font=dict(family="Arial", color="#e9e7f5"),
                         margin=dict(l=10, r=10, t=20, b=10))
    return figure


def india_map(data, metric, district_view=False):
    filename = "india_districts.geojson" if district_view else "india_states.geojson"
    with (ASSETS / filename).open(encoding="utf-8") as stream:
        geojson = json.load(stream)
    data = data.copy()
    if district_view:
        data["map_id"] = data["state"].map(normalize_state) + ":" + data["district"].map(normalize_district)
        data["Place"] = data["district"].map(pretty_name) + ", " + data["state"].map(pretty_name)
    else:
        data["map_id"] = data["state"].map(normalize_state)
        data["Place"] = data["state"].map(pretty_name)
    map_ids = {feature["properties"]["map_id"] for feature in geojson["features"]}
    unmatched = data.loc[~data["map_id"].isin(map_ids), "Place"].tolist()
    data = data[data["map_id"].isin(map_ids)]
    figure = px.choropleth(data, geojson=geojson, featureidkey="properties.map_id",
                          locations="map_id", color=metric, hover_name="Place",
                          hover_data={"map_id": False}, labels=LABELS,
                          color_continuous_scale=["#2a204d", "#7c3aed", "#c4b5fd", "#2dd4bf"])
    figure.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    if data["state"].nunique() > 1:
        figure.update_geos(fitbounds=False, projection_type="mercator",
                           lonaxis_range=[67, 99], lataxis_range=[5, 38])
    figure.update_traces(marker_line_color="#b9abd5", marker_line_width=0.5)
    style_chart(figure, 540)
    figure.update_layout(coloraxis_colorbar=dict(thickness=12, len=0.6))
    return figure, unmatched


def bar_chart(data, name, metric):
    data = data.copy()
    data[name] = data[name].map(pretty_name)
    figure = px.bar(data.sort_values(metric), x=metric, y=name, orientation="h",
                    labels=LABELS, color_discrete_sequence=COLORS)
    figure.update_layout(yaxis_title=None)
    return style_chart(figure, 380)

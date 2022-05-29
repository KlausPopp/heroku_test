import plotly.express as px
import plotly.graph_objects as go
import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
from influxdb_client import InfluxDBClient

import pandas as pd

client = InfluxDBClient(
    url="https://westeurope-1.azure.cloud2.influxdata.com",
    token="TaFEe3NXSIEKqJAISbDFwo6vIQgHbp2HFmTn3N7sRzw5hSZMohYciXeH4uN2ruCH87JONXfEQgPRKv_O70rzbg==",
    org="klaus.popp@ci4rail.com",
)
query_api = client.query_api()
mapbox_token = "pk.eyJ1IjoiY2k0cmFpbCIsImEiOiJjbDNvdDhwZzIwb2JhM2xzNjgweDJiZDl3In0.uyeISrqmcKn_2Tb3ROS8Sw"

app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div(
        [
            html.H4("Vehicle View"),
            dcc.Graph(id="the-map"),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    )
)


@app.callback(Output("the-map", "figure"), Input("interval-component", "n_intervals"))
def update_graph(n):
    df = query_api.query_data_frame(
        """from(bucket: "v-data") 
  |> range(start: -3m)
  |> filter(fn: (r) => r["_measurement"] == "position" or r["_measurement"] == "speed")
  |> filter(fn: (r) => r["_field"] == "lat" or r["_field"] == "lon" or r["_field"] == "vehicle-speed")
  |> aggregateWindow(every: 1s, fn: mean)
  |> fill(usePrevious: true)
  |> last()
  |> group()
  |> pivot(rowKey:["_time", "line", "run"], columnKey: ["_field"], valueColumn: "_value") """
    )
    print(np.dstack((df["vehicle-speed"], df["run"])))
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=df["lat"],
            lon=df["lon"],
            marker={
                "symbol": "bus",
                "color": "red",
                "size": 15,
            },
            mode="markers+text",
            text=df["line"],
            textfont={"family": "Arial", "size": 12, "color": "Black"},
            textposition="bottom right",
            customdata=np.stack((df["vehicle-speed"], df["run"])),
            hovertemplate="Run: %{customdata[1]}<br>Speed: %{customdata[0]} km/h",
        )
    )

    # openstreetmap and other GL JS styles aren't working with text and specific markers
    # fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(
        mapbox={
            "accesstoken": mapbox_token,
            "style": "streets",
            "center": {"lat": 52.4, "lon": -1.5},
            "zoom": 10,
        },
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig["layout"]["uirevision"] = "Hello"  # keep users zoom&pan
    return fig


if __name__ == "__main__":
    app.run_server(debug=False)

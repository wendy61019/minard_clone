import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#準備3個資料框
connection = sqlite3.connect("data/minard.db")
city_df = pd.read_sql("SELECT * FROM cities;", con=connection)
temperature_df = pd.read_sql("SELECT * FROM temperatures;", con=connection)
troop_df = pd.read_sql("SELECT * FROM troops;", con=connection)
connection.close()

#建立雙畫表：在第1列繪製地圖、城市圖、軍隊圖，第2列繪製氣溫圖
fig_dynamic = make_subplots(
    rows=2, cols=1,
    vertical_spacing=0.08,
    row_heights=[0.75, 0.25],
    specs=[[{"type": "map"}], [{"type": "xy"}]],
    subplot_titles=("🗺️ Map of Napoleon's Russian Campaign of 1812 (Dynamic version)", "<b>🌡️ Temperature & Date</b>")
)

#在第1列繪製地圖、軍隊圖
for i in range(len(troop_df) - 1):
    lon_start, lon_end = troop_df.loc[i, 'lonp'], troop_df.loc[i+1, 'lonp']
    lat_start, lat_end = troop_df.loc[i, 'latp'], troop_df.loc[i+1, 'latp']
    survivors = troop_df.loc[i, 'surviv']
    direction = troop_df.loc[i, 'direc']
    line_color = 'rgba(232, 197, 150, 0.9)' if direction == 'A' else 'rgba(38, 38, 38, 0.95)'
    status_text = "前進 (Advance)" if direction == 'A' else "撤退 (Retreat)"
    pixel_width = (survivors / 422000) * 35
    pixel_width = max(pixel_width, 1.5)
    fig_dynamic.add_trace(
        go.Scattermap(
            lon=[lon_start, lon_end],
            lat=[lat_start, lat_end],
            mode='lines',
            line=dict(width=pixel_width, color=line_color),
            hoverinfo='text',
            text=f"狀態: {status_text}<br>兵力: {survivors:,} 人<br>座標: ({lat_start:.1f}, {lon_start:.1f})",
            showlegend=False
        ),
        row=1, col=1
    )
    
#在第1列繪製城市圖
fig_dynamic.add_trace(
    go.Scattermap(
        lon=city_df['lonc'],
        lat=city_df['latc'],
        mode='markers+text',
        marker=dict(size=8, color='rgb(220, 53, 69)'),
        text=city_df['city'],
        textposition='top center',
        hoverinfo='text',
        hovertext=city_df['city'],
        showlegend=False
    ), 
    row=1, col=1
)

#在第2列繪製氣溫圖
temperature_df['temp_c'] = (temperature_df['temp'] * 5 / 4).astype(int)
temp_annotations = temperature_df['temp_c'].astype(str) + "°C (" + temperature_df['date'].fillna("未知日期") + ")"
fig_dynamic.add_trace(
    go.Scatter(
        x=temperature_df['lont'], 
        y=temperature_df['temp_c'],
        mode='lines+markers+text',
        line=dict(color='rgb(165, 42, 42)', width=2, shape='spline'),
        marker=dict(size=6, color='black'),
        text=temp_annotations,
        textposition='bottom center',
        name='氣溫紀錄',
        hoverinfo='x+y'
    ),
    row=2, col=1
)

#調整地圖風格與畫布外觀
fig_dynamic.update_layout(
    height=950, template="plotly_white", showlegend=False,
    map=dict(style="carto-positron", center=dict(lat=54.8, lon=31.0), zoom=4.2),
    xaxis_title="Temperature map with longitude (Align to the map above)",
    yaxis_title="Celsius (°C)"
)
#調整氣溫圖格線
fig_dynamic.update_xaxes(showgrid=True, gridcolor='gray', row=2, col=1)
fig_dynamic.update_yaxes(range=[-45, 5], gridcolor='gray', row=2, col=1)
fig_dynamic.write_html("minard_clone_dynamic.html")
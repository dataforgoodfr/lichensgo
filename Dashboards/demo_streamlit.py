import streamlit as st
import pandas as pd
import my_data.datasets as df
import plotly.graph_objects as go
import numpy as np

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4
# run with : streamlit run Dashboards/demo_streamlit.py

lichen_ecology = df.get_lichen_ecology()

# Debug data
# st.dataframe(df)

# Calculer les proportions des espèces selon leur tolérance à l'anthropisation
artificialisation_proportions = lichen_ecology['poleotolerance'].value_counts(normalize=True) * 100

# # Dataviz charts
fig1 = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = artificialisation_proportions["intermediate"],
    mode = "gauge+number",
    title = {'text': "Degré d'artificialisation"},
    gauge = {'axis': {'range': [0, 100], 'dtick': 25},
             'bar': {'color': "#000000"},
             'steps' : [
                 {'range': [0, 25], 'color': "#E3D7FF"},
                 {'range': [25, 50], 'color': "#AFA2FF"},
                 {'range': [50, 75], 'color': "#7A89C2"},
                 {'range': [75, 100], 'color': "#72788D"}
                 ],
             'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': artificialisation_proportions["intermediate"]}
             }))

x_values = [10, 8, 6, 5, 4, 3, 2, 1]
y_values = ["Punctelia", "Physcia tenella", "Flavoparmelia", "Espèce 4", "Espèce 5", "Espèce 6", "Espèce 7", "Espèce 8"]
x_values.reverse()
y_values.reverse()

fig2 = go.Figure(go.Bar(
            x=x_values,
            y=y_values,
            orientation='h'))

fig2.update_layout(
    title="Espèces observées sur le site sélectionné",
    xaxis_title="Nombre de quadrat",
    yaxis_title="",
    yaxis=dict(tickmode='array', tickvals=[0, 1, 2, 3, 4, 5, 6, 7],
               ticktext=["Punctelia", "Physcia tenella", "Flavoparmelia", "Espèce 4", "Espèce 5", "Espèce 6", "Espèce 7", "Etc."])
)

plot_bgcolor = "#def"
quadrant_colors = [plot_bgcolor, "#f25829", "#f2a529", "#eff229", "#2bad4e"] 
n_quadrants = len(quadrant_colors) - 1

current_value = 19
min_value = 0
max_value = 50
hand_length = np.sqrt(2) / 4
hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

## Version 3 non retenue du code python
# fig3 = go.Figure(
#     data=[
#         go.Pie(
#             values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
#             rotation=90,
#             hole=0.5,
#             marker_colors=quadrant_colors,
#             textinfo="text",
#             hoverinfo="skip",
#         ),
#     ],
#     layout=go.Layout(
#         showlegend=False,
#         margin=dict(b=0,t=10,l=10,r=10),
#         width=450,
#         height=450,
#         paper_bgcolor=plot_bgcolor,
#         annotations=[
#             go.layout.Annotation(
#                 text=f"<b>Degrés d'artificialisation:</b><br>{current_value} %",
#                 x=0.5, xanchor="center", xref="paper",
#                 y=0.25, yanchor="bottom", yref="paper",
#                 showarrow=False,
#             )
#         ],
#         shapes=[
#             go.layout.Shape(
#                 type="circle",
#                 x0=0.48, x1=0.52,
#                 y0=0.48, y1=0.52,
#                 fillcolor="#333",
#                 line_color="#333",
#             ),
#             go.layout.Shape(
#                 type="line",
#                 x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
#                 y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
#                 line=dict(color="#333", width=4)
#             )
#         ]
#     )
# )

# Display streamlit
st.title("Dataviz POC")
tab1, tab2, tab3= st.tabs(["Gauge", "Histogram", "df debug"])
with tab1:
    st.write("**Mode de calcul**`df['poleotolerance'].value_counts(normalize=True) * 100`")
    st.plotly_chart(fig1)

with tab2:
    st.plotly_chart(fig2)

with tab3:
    st.write("Debug du dataset")
    # st.dataframe(df)
    
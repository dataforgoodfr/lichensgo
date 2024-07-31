import streamlit as st
import pandas as pd
import my_data.datasets as df
import plotly.graph_objects as go
import numpy as np

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4
# run with : streamlit run Dashboards/demo_streamlit.py

# Finalement > prendre les données issue de la vue
lichen_ecology = df.get_lichen_ecology()
lichen_frequency = df.get_lichen_frequency()

# Calcul somme des fréquences
def calc_frequences(df):
    df_agg = df.groupby("main_lichenspecies").agg({
        "id": "first",
        "frequency": "sum"
    }).reset_index()

    return df_agg

calc_freq = calc_frequences(lichen_frequency)
calc_freq = calc_freq[["main_lichenspecies", "frequency"]]

def deg_artif(id_site: int, species_name : str):
    # Calcul filtrable
    freq = lichen_frequency[lichen_frequency["id"] == id_site]["frequency"].values[0]
    freq_g = calc_freq[calc_freq["main_lichenspecies"] == species_name]["frequency"].values[0] 

    return round(freq / freq_g * 100, 2)


# Sélection du site 
id_site = st.selectbox(
    "Sur quel site voulez-vous ?",
    lichen_frequency["id"],
    index=None,
    placeholder="site n°",
)

# Sélection des espèces 
species_name = st.selectbox(
    "Sur quel espèce voulez-vous ?",
    calc_freq["main_lichenspecies"],
    index=None,
    placeholder="Je sélectionne l'espèce...",
)

# Affichage des éléments
if id_site and species_name != None:
    pass
else:
    id_site = 460
    species_name = "Physcia aipolia/stellaris"
# le calcul
artificialisation_proportions = deg_artif(id_site, species_name)

# # Dataviz charts
fig1 = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = artificialisation_proportions,
    mode = "gauge+number",
    title = {'text': "Degré d'artificialisation"},
    gauge = {'axis': {'range': [0, 100], 'dtick': 25},
             'bar': {'color': "#000000"},
             'steps' : [
                #  {'range': [0, 25], 'color': "#E3D7FF"},
                #  {'range': [25, 50], 'color': "#AFA2FF"},
                #  {'range': [50, 75], 'color': "#7A89C2"},
                #  {'range': [75, 100], 'color': "#72788D"}
                 {'range': [0, 25], 'color': "green"},
                 {'range': [25, 50], 'color': "yellow"},
                 {'range': [50, 75], 'color': "orange"},
                 {'range': [75, 100], 'color': "red"}
                 ],
             'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': artificialisation_proportions}
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

# Display streamlit
st.title("Dataviz POC")
tab1, tab2, tab3= st.tabs(["Gauge", "Histogram", "df Fréquences"])
with tab1:
    st.write(f"Degrés d'artificialisation sur le site n°**{id_site}** pour l'espèce **{species_name}**")
    st.plotly_chart(fig1)

with tab2:
    st.plotly_chart(fig2)

with tab3:
    st.write("les données de fréquences")
    st.write(calc_freq)

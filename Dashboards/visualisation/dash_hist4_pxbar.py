import pandas as pd
import numpy as np

import sys
from pathlib import Path

import plotly.express as px

from dash import Dash, dcc, html
from dash.dependencies import Output, Input

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data


# Initialize Dash app
app = Dash(__name__)

# Load datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()

# group by species' type + add a column with the count occurence
df_grouped=(
    lichen_df
    .groupby("species_id", as_index=False)
    .agg(count_col=pd.NamedAgg(column="species_id", aggfunc="count"))
)

# concatenate dataframe "df_grouped" with the lichen species' names
df_grouped_species=pd.concat([df_grouped, lichen_species_df.loc[:,"name"]], axis=1)

# sort based on occurence 
# (note): update_xaxes(categoryorder="total descending") does not work
df_grouped_species=(
    df_grouped_species
    .sort_values(by="count_col", ascending=False, ignore_index=True)
)

# Define app layout 
app.layout = html.Div([
    html.H1("Select the Lichen's species"),
    dcc.Dropdown(id="dropdown_Lichen",
                 options=lichen_species_df["name"].unique(),
                 value=["Xanthoria parietina"]
                 ),
    dcc.Graph(id="hist4")
])

# Define callback to update graph
@app.callback(
    Output("hist4", "figure"),
    Input("dropdown_Lichen", "value")
)
def hist4_interactive(Lichen_selected):

    # index in "df_grouped_species" corresponding to the selected species
    idx=df_grouped_species["name"].loc[lambda x: x==Lichen_selected].index

    # adjust the color based on the selected species
    color_discrete_sequence=['#ec7c34']*len(df_grouped_species)
    color_discrete_sequence[int(idx[0])]='#609cd4'

    hist4=px.bar(
        df_grouped_species, 
        x="count_col", 
        y="name",
        orientation="h",
        color="name",
        color_discrete_sequence=color_discrete_sequence,
        # width=1500,
        # height=800,
        title="Espèces les plus observées par les observateurs Lichens GO"
    )

    # remove the legend
    hist4.update(layout_showlegend=False)

    # update the title 
    hist4.update_layout(
        title_font=dict(color="grey",size=24),
        title={"x": .5,"y": .95,"xanchor": "center"},
        plot_bgcolor='white',
        paper_bgcolor="white"
    )

    # update axes 
    hist4.update_xaxes(
        title="Count",
        showline=True,
        linecolor='black',
        gridcolor="black",
    )

    hist4.update_yaxes(
        title="",
        showline=True,
        linecolor='black',
    )
    return hist4

# Run the app
if __name__ == "main":
    app.run(debug=True, host="127.0.0.1" ,port=8050)
    #app.run()
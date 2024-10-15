import plotly.express as px
import plotly.graph_objects as go
from Dashboards.constants import BASE_COLOR_PALETTE, PASTEL_COLOR_PALETTE, PLOTLY_LAYOUT, MAP_SETTINGS


def create_map(filtered_df, selected_map_column, zoom, center):
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="localisation_lat",
        lon="localisation_long",
        color=selected_map_column,
        hover_name="date_obs",
        hover_data=["localisation_lat", "localisation_long"],
        mapbox_style="open-street-map",
        color_discrete_map=MAP_SETTINGS[selected_map_column]["color_map"],
    )

    fig_map.update_layout(
        **PLOTLY_LAYOUT,
        mapbox_zoom=zoom,
        mapbox_center=center,
    )

    return fig_map

def create_hist1_nb_species(observation_with_vdl_df, nb_species_clicked):
    hist1 = px.histogram(
        observation_with_vdl_df,
        x='nb_species',
        color_discrete_sequence=BASE_COLOR_PALETTE
        )

    hist1.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="Nombre d'espèces",
        yaxis_title="Nombre de sites",
        yaxis_showgrid=True,
        bargap=0.1,
    )

    # Add vertical line for the clicked number of species
    if nb_species_clicked:
        hist1.add_shape(
            go.layout.Shape(
                type="line",
                x0=nb_species_clicked, x1=nb_species_clicked,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color='red', width=2, dash="dot")
            )
        )

    return hist1


def create_hist2_vdl(observation_with_vdl_df, vdl_clicked):
    hist2 = px.histogram(
        observation_with_vdl_df,
        x='VDL',
        color_discrete_sequence=BASE_COLOR_PALETTE
    )

    hist2.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="Valeur de Diversité Lichénique (VDL)",
        yaxis_title="Nombre de sites",
        yaxis_showgrid=True,
        bargap=0.1,
    )

    # Add vertical line for the clicked VDL value
    if vdl_clicked:
        hist2.add_shape(
            go.layout.Shape(
                type="line",
                x0=vdl_clicked, x1=vdl_clicked,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color='red', width=2, dash="dot")
            )
        )

    return hist2


def create_hist3(lichen_frequency_df):

    hist3 = px.bar(
        lichen_frequency_df,
        x="nb_lichen",
        y="unique_name",
        orientation="h",
        color_discrete_sequence=BASE_COLOR_PALETTE,
    )

    hist3.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="Nombre",
        yaxis_title="",
        xaxis_showgrid=True,
    )

    # Update hover template
    hist3.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br><br>"
            "<b>Nombre:</b> %{x}<br>"
            "<b>Nord:</b> %{customdata[0]:<2}<br>"
            "<b>Sud:</b> %{customdata[1]:<2}<br>"
            "<b>Ouest:</b> %{customdata[2]:<2}<br>"
            "<b>Est:</b> %{customdata[3]:<2}<br>"
            "<extra></extra>"
        ),
        customdata=lichen_frequency_df[['nb_lichen_N', 'nb_lichen_S', 'nb_lichen_O', 'nb_lichen_E']].values
    )

    return hist3

## Gauge charts

def create_gauge_chart(value, title=None):
    fig = go.Figure(
        go.Indicator(
            domain={"x": [0, 1], "y": [0, 1]},
            value=value,
            number={"suffix": "%", "font": {"size": 18}},
            mode="gauge+number",
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100], "dtick": 25},
                'bar': {'color': "rgba(0,0,0,1)", 'thickness': 0.3},
                "steps": [
                    {'range': [0, 25], 'color': "rgba(34, 139, 34, 0.7)"},
                    {'range': [25, 50], 'color': "rgba(255, 215, 0, 0.7)"},
                    {'range': [50, 75], 'color': "rgba(255, 140, 0, 0.7)"},
                    {'range': [75, 100], 'color': "rgba(255, 69, 0, 0.7)"}
                ],
                "threshold": {
                    "line": {"color": "rgba(0,0,0,1)", "width": 3},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT
    )

    return fig


## Histograms for species

def create_hist4(count_lichen_per_species_df, user_selection_species_id):
    # Find the index of the selected species ID in the merged table
    user_selection_idx = count_lichen_per_species_df[count_lichen_per_species_df["species_id"] == user_selection_species_id].index

    # Adjust the color of the selected specie to be darker
    pastel_color = PASTEL_COLOR_PALETTE[0]
    selected_color = BASE_COLOR_PALETTE[0]
    color_hist4 = [pastel_color] * len(count_lichen_per_species_df)
    color_hist4[int(user_selection_idx[0])] = selected_color

    # Bar plot
    hist4 = px.bar(
        count_lichen_per_species_df,
        x="count",
        y="name",
        orientation="h",
        color="name",
        color_discrete_sequence=color_hist4,
        )

    # Update layout
    hist4.update_layout(
        **PLOTLY_LAYOUT,
        showlegend=False,
    )

    # Update axes
    hist4.update_xaxes(
        title_text="Nombre",
        showgrid=True,
    )
    hist4.update_yaxes(
        title="",
        # tickfont=dict(size=10)  # Adjust tick font size
    )
    hist4.update_traces(
        hovertemplate="<b>%{y}</b><br><b>Nombre:</b> %{x}<extra></extra>"
    )

    return hist4

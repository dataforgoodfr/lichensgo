import plotly.express as px
import plotly.graph_objects as go
from dashboard.constants import BASE_COLOR_PALETTE, PASTEL_COLOR_PALETTE, PLOTLY_LAYOUT, MAP_COLOR_PALETTES


"""
Create a blank figure for initialisation

"""
def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(
        template=None,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig

def create_map_observations(filtered_df, map_column_selected, zoom, center, map_style, observation_clicked=None):

    fig_map = px.scatter_map(
        filtered_df,
        lat='localisation_lat',
        lon='localisation_long',
        color=map_column_selected,
        hover_name='date_obs',
        hover_data={
            'localisation_lat': True,
            'localisation_long': True,
            'nb_species': True,
            'nb_species_cat': False,
            'VDL': True,
            'VDL_cat': False,
            'deg_toxitolerance': True,
            'deg_toxitolerance_cat': False,
            'deg_eutrophication': True,
            'deg_eutrophication_cat': False,
            'deg_acidity': True,
            'deg_acidity_cat': False,
        },
        labels={
            'date_obs': 'Date d\'observation',
            'localisation_lat': 'Latitude ',
            'localisation_long': 'Longitude ',
            'nb_species': 'Nombre d\'espèces ',
            'nb_species_cat': 'Nombre d\'espèces ',
            'VDL': 'Valeur de Diversité Lichénique ',
            'VDL_cat': 'Valeur de Diversité Lichénique ',
            'deg_toxitolerance': 'Espèces toxitolérantes (%) ',
            'deg_toxitolerance_cat': 'Espèces toxitolérantes',
            'deg_eutrophication': 'Espèces eutrophes (%) ',
            'deg_eutrophication_cat': 'Espèces eutrophes ',
            'deg_acidity' : 'Espèces acidophiles (%) ',
            'deg_acidity_cat' : 'Espèces acidophiles',
        },
        map_style=map_style,
        color_discrete_map=MAP_COLOR_PALETTES[map_column_selected],
        category_orders={map_column_selected: list(MAP_COLOR_PALETTES[map_column_selected].keys())}, # order the legend in the same order as the color palette
    )

    if observation_clicked is not None:

        observation_clicked_color = MAP_COLOR_PALETTES[map_column_selected][observation_clicked[map_column_selected]]

        fig_map.add_trace(
            go.Scattermap(
                lat=[observation_clicked['localisation_lat']],
                lon=[observation_clicked['localisation_long']],
                mode='markers',
                marker=go.scattermap.Marker(
                    size=13,
                    color=observation_clicked_color,
                ),
                hoverinfo='skip',  # Hide the hover info, to use the one from the main trace
                showlegend=False
            )
        )

    fig_map.update_layout(
        PLOTLY_LAYOUT,
        margin=dict(l=0, r=0, t=0, b=0),
        map_zoom=zoom,
        map_center=center,
        legend=dict(
            x=0.02,  # Position the legend on the map
            y=0.02,
            bgcolor='rgba(255, 255, 255, 0.8)',  # Semi-transparent background
            bordercolor='grey',
            borderwidth=1.5,
        ),
    )

    return fig_map

def create_map_species_present(filtered_df, map_column_selected, zoom, center, map_style):

    fig_map = px.scatter_map(
        filtered_df,
        lat='localisation_lat',
        lon='localisation_long',
        color=map_column_selected,
        hover_name='date_obs',
        hover_data={
            'localisation_lat': True,
            'localisation_long': True,
            'selected_species_present': True,
        },
        labels={
            'date_obs': 'Date d\'observation',
            'localisation_lat': 'Latitude',
            'localisation_long': 'Longitude',
            'selected_species_present': 'Espèce présente',
        },
        map_style=map_style,
        color_discrete_map=MAP_COLOR_PALETTES[map_column_selected],
    )

    fig_map.update_layout(
        PLOTLY_LAYOUT,
        margin=dict(l=0, r=0, t=0, b=0),
        map_zoom=zoom,
        map_center=center,
        legend=dict(
            x=0.02,  # Position the legend on the map
            y=0.02,
            bgcolor='rgba(255, 255, 255, 0.8)',  # Semi-transparent background
            bordercolor='grey',
            borderwidth=1.5,
        ),
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
        xaxis_title="Nombre d\'espèces",
        yaxis_title="Nombre de sites",
        yaxis_showgrid=True,
        bargap=0.1,
    )

    # Update hover template
    hist1.update_traces(
        hovertemplate=(
            "<b>Nombre d'espèces:</b> %{x}<br>"
            "<b>Nombre de sites:</b> %{y}<br>"
            "<extra></extra>"
        )
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

    # Update hover template
    hist2.update_traces(
        hovertemplate=(
            "<b>VDL:</b> %{x}<br>"
            "<b>Nombre de sites:</b> %{y}<br>"
            "<extra></extra>"
        )
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
        x="nb_lichen_ratio",
        y="unique_name",
        orientation="h",
        color_discrete_sequence=BASE_COLOR_PALETTE,
    )

    hist3.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="% de quadrats",
        yaxis_title="",
        xaxis_showgrid=True,
        xaxis_tickformat=".0%",
        xaxis=dict(
            range=[0, 1.1],
            dtick=0.25  # Set x-axis ticks every 25%
        )
    )

    # Update hover template
    hist3.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br><br>"
            "<b>Pourcentage:</b> %{x}<br>"
            "<b>Nombre:</b> %{customdata[0]}<br>"
            "<b>Nord:</b> %{customdata[1]}<br>"
            "<b>Sud:</b> %{customdata[2]}<br>"
            "<b>Ouest:</b> %{customdata[3]}<br>"
            "<b>Est:</b> %{customdata[4]}<br>"
            "<extra></extra>"
        ),
        customdata=lichen_frequency_df[['nb_lichen','nb_lichen_N', 'nb_lichen_S', 'nb_lichen_O', 'nb_lichen_E']].values
    )

    return hist3


def create_pie_thallus(grouped_table_by_observation_and_thallus_df):

    # Capitalize the thallus names
    capital_grouped_table_by_observation_and_thallus_df = grouped_table_by_observation_and_thallus_df.copy()
    capital_grouped_table_by_observation_and_thallus_df['thallus'] = grouped_table_by_observation_and_thallus_df['thallus'].str.capitalize()

    pie_thallus = px.pie(
        capital_grouped_table_by_observation_and_thallus_df,
        names="thallus",
        values="nb_lichen_id",
        color_discrete_sequence=BASE_COLOR_PALETTE[::3],
    )

    pie_thallus.update_layout(
        **PLOTLY_LAYOUT,
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",  # Anchor the legend to the bottom
            y=1.1,  # Position the legend at the top
            xanchor="center",  # Center the legend horizontally
            x=0.5  # Center the legend horizontally
        ),
    )

    # Update hover template and text template
    pie_thallus.update_traces(
        hovertemplate="<b>%{label}</b><br><b>Nombre:</b> %{value}<extra></extra>",
        texttemplate="%{percent:.0%}"  # Format displayed values as percentages with no decimal places
    )

    return pie_thallus

## Gauge charts

def create_gauge_chart(value, intervals, color_scale):

    percentage_value = value * 100

    fig = go.Figure(
        go.Indicator(
            domain={"x": [0, 1], "y": [0, 1]},
            value=percentage_value,
            number={"suffix": "%",
                    "valueformat": ".0f", # Format the value as a number with no decimals
                    "font":
                        {"size": 24 ,
                         "color": find_color(percentage_value, intervals=intervals, color_scale=color_scale)
                         }
                    },
            mode="gauge+number",
            gauge={
                "axis": {"range": [0, 100], "dtick": 25},
                'bar': {'color': "rgba(60, 60, 60, 1)", 'thickness': 0.4},
                "steps": [
                    {'range': intervals[i:i+2], 'color': color_scale[i]} for i in range(len(intervals) - 1)
                ],
                "threshold": {
                    "line": {"color": "rgba(60, 60, 60, 1)", "width": 3},
                    "thickness": 0.75,
                    "value": percentage_value,
                },
            },
        )
    )

    fig.update_layout(
        PLOTLY_LAYOUT,
        margin=dict(l=0, r=0, t=20, b=10),
    )

    return fig


def find_interval(value, intervals):
    for i in range(len(intervals) - 1):
        if intervals[i] <= value < intervals[i + 1]:
            return i

    if value == intervals[-1]:
        return len(intervals) - 2 # Return the last interval index if the value is equal to the last element

    if value >= intervals[-1]:
        return len(intervals) - 1

    return None

def find_color(value, intervals, color_scale):
    if len(intervals) != len(color_scale) + 1:
        raise ValueError("The number of intervals should be equal to the number of colors + 1")

    color_idx = find_interval(value, intervals)
    return color_scale[color_idx]

def create_kpi(value, title=None, intervals=None, color_scale=None):

    if intervals is None:
        intervals = [0, 25, 50, 75, 100.5]
    if color_scale is None:
        color_scale = ['green', 'yellow', 'orange', 'red']

    color = find_color(value, intervals, color_scale)

    indicator = go.Indicator(
        value=value,
        number={"suffix": "%", "font": {"color": color, "size": 50}},
        mode="number",
        title={"text": title},
    )

    fig = go.Figure(indicator)

    fig.update_layout(
        PLOTLY_LAYOUT,
        margin=dict(l=0, r=0, t=0, b=0),
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

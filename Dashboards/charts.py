import plotly.express as px
from constants import BASE_COLOR_PALETTE, PASTEL_COLOR_PALETTE, ORIENTATIONS, ORIENTATIONS_MAPPING, SQUARE_COLUMNS, BODY_STYLE, BODY_FONT_FAMILY, BODY_FONT_COLOR, PLOTLY_LAYOUT, PLOTLY_HOVER_STYLE

def create_hist3(lichen_frequency_df):
   # Create the bar plot
    hist3 = px.bar(
        lichen_frequency_df,
        x="nb_lichen",
        y="unique_name",
        orientation="h",
        color_discrete_sequence=BASE_COLOR_PALETTE,
    )

    # Update layout
    hist3.update_layout(
        **PLOTLY_LAYOUT,
        legend_title_text="Orientation",
    )

    # Update axes
    hist3.update_xaxes(
        title_text="Nombre",
        showgrid=True,
        # tickfont=dict(size=14)
    )
    hist3.update_yaxes(
        title_text="",
        # tickfont=dict(size=14)
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
        # title="Espèces les plus observées par les observateurs Lichens GO"
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

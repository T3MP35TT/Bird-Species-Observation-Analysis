import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bird Habitat Analytics",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .main-title {
        font-size: 34px;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .subtitle {
        opacity: 0.70;
        font-size: 15px;
        margin-bottom: 18px;
    }

    div.block-container { 
    padding-top: 3rem; 
    padding-bottom: 2rem; 
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        min-height: 105px !important;
        box-sizing: border-box !important;
    }

    label[data-testid="stMetricLabel"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    label[data-testid="stMetricLabel"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    label[data-testid="stMetricLabel"] p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    label[data-testid="stMetricLabel"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    label[data-testid="stMetricLabel"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricValue"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }


    /* ========================================================
       SECTION HEADINGS
       ======================================================== */

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 10px;
    }


    /* ========================================================
       INSIGHT BOX
       ======================================================== */

    .insight-box {
        background-color: var(--secondary-background-color);
        border-left: 4px solid #4ea5ff;
        border-radius: 8px;
        padding: 13px 16px;
        margin: 8px 0 18px 0;
    }

    .insight-title {
        font-weight: 700;
        margin-bottom: 4px;
    }

    .insight-text {
        font-size: 14px;
        opacity: 0.82;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    connection = sqlite3.connect(
        "database/bird_observations.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM bird_observations",
        connection
    )

    connection.close()


    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    boolean_columns = [
        "PIF_Watchlist_Status",
        "Regional_Stewardship_Status",
        "Flyover_Observed"
    ]

    for col in boolean_columns:

        if col in df.columns:

            if df[col].dtype == "object":

                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .map({
                        "true": True,
                        "false": False,
                        "1": True,
                        "0": False
                    })
                    .fillna(False)
                )

            else:
                df[col] = df[col].astype(bool)


    return df


bird_df = load_data()


# ============================================================
# CONSTANTS
# ============================================================

MONTH_ORDER = [
    "May",
    "June",
    "July"
]

FOREST_COLOR = "#2563EB"
GRASSLAND_COLOR = "#16A34A"

HABITAT_COLORS = {
    "Forest": FOREST_COLOR,
    "Grassland": GRASSLAND_COLOR
}


# ============================================================
# PLOTLY THEME HELPER
# ============================================================

def style_chart(
    fig,
    height=380,
    showlegend=True,
    x_title=None,
    y_title=None
):

    fig.update_layout(
        height=height,
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            size=12
        ),
        title=dict(
            x=0,
            xanchor="left",
            font=dict(
                size=17
            )
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ) if showlegend else dict(
            orientation="h"
        ),
        margin=dict(
            l=55,
            r=25,
            t=70,
            b=55
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        title=x_title,
        showline=True,
        linewidth=1,
        linecolor="#CBD5E1"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.20)",
        zeroline=False,
        title=y_title,
        showline=False
    )

    return fig


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🐦 Bird Habitat Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive analysis of bird observations across Forest and Grassland habitats'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Filters")

st.sidebar.caption(
    "Explore the bird observation dataset using the filters below."
)


min_date = bird_df["Date"].min().date()
max_date = bird_df["Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range_final"
)

if len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
else:
    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date)


# Habitat

habitat_options = sorted(
    bird_df["Habitat"]
    .dropna()
    .unique()
    .tolist()
)

selected_habitats = st.sidebar.multiselect(
    "🌳 Habitat",
    options=habitat_options,
    default=habitat_options,
    key="habitat_filter_final"
)


# Month

available_months = [
    month
    for month in MONTH_ORDER
    if month in bird_df["Month_Name"].unique()
]

selected_months = st.sidebar.multiselect(
    "📆 Month",
    options=available_months,
    default=available_months,
    key="month_filter_final"
)


# Species

species_options = sorted(
    bird_df["Common_Name"]
    .dropna()
    .unique()
    .tolist()
)

selected_species = st.sidebar.multiselect(
    "🐦 Species",
    options=species_options,
    default=[],
    placeholder="All species",
    key="species_filter_final"
)


# Plot

plot_options = sorted(
    bird_df["Plot_Name"]
    .dropna()
    .unique()
    .tolist()
)

selected_plots = st.sidebar.multiselect(
    "📍 Plot",
    options=plot_options,
    default=[],
    placeholder="All plots",
    key="plot_filter_final"
)


# Identification method

id_options = sorted(
    bird_df["ID_Method"]
    .dropna()
    .unique()
    .tolist()
)

selected_id_methods = st.sidebar.multiselect(
    "🔭 Identification Method",
    options=id_options,
    default=id_options,
    key="id_filter_final"
)


# Conservation

conservation_filter = st.sidebar.selectbox(
    "🛡️ Conservation Status",
    [
        "All Observations",
        "PIF Watchlist",
        "Regional Stewardship",
        "Either Conservation Status"
    ],
    key="conservation_filter_final"
)


st.sidebar.divider()

st.sidebar.caption(
    f"Dataset: {len(bird_df):,} observations"
)

st.sidebar.caption(
    f"Species: {bird_df['Scientific_Name'].nunique():,}"
)

st.sidebar.caption(
    f"Plots: {bird_df['Plot_Name'].nunique():,}"
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = bird_df[
    (bird_df["Date"] >= start_date)
    &
    (bird_df["Date"] <= end_date)
    &
    (bird_df["Habitat"].isin(selected_habitats))
    &
    (bird_df["Month_Name"].isin(selected_months))
    &
    (bird_df["ID_Method"].isin(selected_id_methods))
].copy()


if selected_species:

    filtered_df = filtered_df[
        filtered_df["Common_Name"].isin(
            selected_species
        )
    ]


if selected_plots:

    filtered_df = filtered_df[
        filtered_df["Plot_Name"].isin(
            selected_plots
        )
    ]


if conservation_filter == "PIF Watchlist":

    filtered_df = filtered_df[
        filtered_df["PIF_Watchlist_Status"] == True
    ]


elif conservation_filter == "Regional Stewardship":

    filtered_df = filtered_df[
        filtered_df["Regional_Stewardship_Status"] == True
    ]


elif conservation_filter == "Either Conservation Status":

    filtered_df = filtered_df[
        (
            filtered_df["PIF_Watchlist_Status"] == True
        )
        |
        (
            filtered_df["Regional_Stewardship_Status"] == True
        )
    ]


if filtered_df.empty:

    st.warning(
        "No observations match the selected filters. "
        "Try expanding your selections."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_observations = len(filtered_df)

unique_species = (
    filtered_df["Scientific_Name"]
    .nunique()
)

forest_count = len(
    filtered_df[
        filtered_df["Habitat"] == "Forest"
    ]
)

grassland_count = len(
    filtered_df[
        filtered_df["Habitat"] == "Grassland"
    ]
)

conservation_count = len(
    filtered_df[
        (
            filtered_df["PIF_Watchlist_Status"] == True
        )
        |
        (
            filtered_df["Regional_Stewardship_Status"] == True
        )
    ]
)


# ============================================================
# TOP KPI ROW
# ============================================================

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "🐦 Total Observations",
    f"{total_observations:,}"
)

k2.metric(
    "🧬 Unique Species",
    f"{unique_species:,}"
)

k3.metric(
    "🌲 Forest",
    f"{forest_count:,}"
)

k4.metric(
    "🌾 Grassland",
    f"{grassland_count:,}"
)

k5.metric(
    "🛡️ Conservation",
    f"{conservation_count:,}"
)


st.caption(
    f"Showing **{total_observations:,} observations** "
    f"from **{start_date.strftime('%d %b %Y')}** "
    f"to **{end_date.strftime('%d %b %Y')}**"
)

st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "🐦 Species",
        "🌤️ Environment & Detection",
        "🛡️ Conservation & Plots"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">Habitat Overview</div>',
        unsafe_allow_html=True
    )

    habitat_counts = (
        filtered_df
        .groupby("Habitat")
        .size()
        .reset_index(
            name="Observations"
        )
    )

    habitat_counts["Percentage"] = (
        habitat_counts["Observations"]
        / total_observations
        * 100
    )


    # Insight

    if len(habitat_counts) > 0:

        top_habitat = (
            habitat_counts
            .sort_values(
                "Observations",
                ascending=False
            )
            .iloc[0]
        )

        st.markdown(
            f"""
            <div class="insight-box">
                <div class="insight-title">💡 Key Insight</div>
                <div class="insight-text">
                    <b>{top_habitat["Habitat"]}</b> accounts for
                    <b>{int(top_habitat["Observations"]):,}</b>
                    observations
                    ({top_habitat["Percentage"]:.1f}% of the current selection).
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # HABITAT DISTRIBUTION
    # --------------------------------------------------------

    with col1:

        fig = px.bar(
            habitat_counts,
            x="Habitat",
            y="Observations",
            color="Habitat",
            text="Observations",
            color_discrete_map=HABITAT_COLORS,
            title="Observations by Habitat"
        )

        fig.update_traces(
            textposition="outside",
            textfont=dict(
                size=12
            ),
            marker_line_width=0
        )

        fig = style_chart(
            fig,
            height=380,
            showlegend=False,
            x_title=None,
            y_title="Observations"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # --------------------------------------------------------
    # HABITAT SHARE
    # --------------------------------------------------------

    with col2:

        fig = px.pie(
            habitat_counts,
            names="Habitat",
            values="Observations",
            hole=0.58,
            color="Habitat",
            color_discrete_map=HABITAT_COLORS,
            title="Observation Share by Habitat"
        )

        fig.update_traces(
            textposition="outside",
            textinfo="label+percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Observations: %{value:,}<br>"
                "Share: %{percent}<extra></extra>"
            )
        )

        fig.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(
                l=20,
                r=20,
                t=70,
                b=20
            ),
            title=dict(
                x=0
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.08,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # --------------------------------------------------------
    # MONTHLY OBSERVATION TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Observation Trends</div>',
        unsafe_allow_html=True
    )

    monthly = (
        filtered_df
        .groupby(
            [
                "Month_Number",
                "Month_Name",
                "Habitat"
            ]
        )
        .size()
        .reset_index(
            name="Observations"
        )
        .sort_values(
            "Month_Number"
        )
    )
    # --------------------------------------------------------
    # MONTHLY OBSERVATION TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title"></div>',
        unsafe_allow_html=True
    )

    monthly = (
        filtered_df
        .groupby(
            [
                "Month_Number",
                "Month_Name",
                "Habitat"
            ]
        )
        .size()
        .reset_index(
            name="Observations"
        )
        .sort_values(
            "Month_Number"
        )
    )


    # --------------------------------------------------------
    # GROUPED COLUMN CHART
    # --------------------------------------------------------

    fig = px.bar(
        monthly,
        x="Month_Name",
        y="Observations",
        color="Habitat",
        barmode="group",
        text="Observations",

        category_orders={
            "Month_Name": MONTH_ORDER
        },

        color_discrete_map={
            "Forest": "#2563EB",
            "Grassland": "#16A34A"
        },

        title="Monthly Observations by Habitat"
    )


    # --------------------------------------------------------
    # BAR APPEARANCE
    # --------------------------------------------------------

    fig.update_traces(

        texttemplate="%{y:,}",

        textposition="outside",

        textfont=dict(
            size=12
        ),

        marker_line_width=0,

        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{fullData.name}: %{y:,} observations"
            "<extra></extra>"
        )
    )


    # --------------------------------------------------------
    # CHART LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        height=390,

        margin=dict(
            l=20,
            r=25,
            t=65,
            b=45
        ),

        bargap=0.35,

        bargroupgap=0.08,

        legend=dict(
            title=None,

            orientation="h",

            yanchor="bottom",
            y=1.02,

            xanchor="right",
            x=1,

            font=dict(
                size=12
            )
        ),

        xaxis=dict(

            title=None,

            showgrid=False,

            showline=False,

            zeroline=False,

            categoryorder="array",

            categoryarray=MONTH_ORDER,

            tickfont=dict(
                size=13
            )
        ),

        yaxis=dict(

            title=None,

            showgrid=True,

            gridcolor="rgba(100,116,139,0.10)",

            gridwidth=1,

            zeroline=False,

            rangemode="tozero",

            tickformat=",",

            tickfont=dict(
                size=10
            )
        ),

        plot_bgcolor="rgba(0,0,0,0)",

        paper_bgcolor="rgba(0,0,0,0)",

        hovermode="x unified"
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


    # --------------------------------------------------------
    # KEY TREND INSIGHT
    # --------------------------------------------------------

    if len(monthly) > 0:

        # Find month with highest total observations
        monthly_totals = (
            monthly
            .groupby(
                "Month_Name"
            )["Observations"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        peak_month = (
            monthly_totals.index[0]
        )

        peak_month_total = int(
            monthly_totals.iloc[0]
        )


        # Get Forest observations for peak month
        forest_peak = monthly[
            (
                (monthly["Month_Name"] == peak_month)
                &
                (monthly["Habitat"] == "Forest")
            )
        ]["Observations"]


        # Get Grassland observations for peak month
        grassland_peak = monthly[
            (
                (monthly["Month_Name"] == peak_month)
                &
                (monthly["Habitat"] == "Grassland")
            )
        ]["Observations"]


        if (
            len(forest_peak) > 0
            and
            len(grassland_peak) > 0
        ):

            forest_value = int(
                forest_peak.iloc[0]
            )

            grassland_value = int(
                grassland_peak.iloc[0]
            )

            difference = abs(
                forest_value -
                grassland_value
            )


            if forest_value > grassland_value:

                dominant_habitat = "Forest"

            elif grassland_value > forest_value:

                dominant_habitat = "Grassland"

            else:

                dominant_habitat = "both habitats equally"


            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{peak_month}</b> recorded the highest overall
                    observation activity with
                    <b>{peak_month_total:,}</b> observations.
                    <b>{dominant_habitat}</b> had the higher observation
                    count that month, with a difference of
                    <b>{difference:,}</b> observations.
                </div>
                """,
                unsafe_allow_html=True
            )


        else:

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{peak_month}</b> recorded the highest overall
                    observation activity with
                    <b>{peak_month_total:,}</b> observations.
                </div>
                """,
                unsafe_allow_html=True
            )
     # --------------------------------------------------------
    # DAILY OBSERVATION PATTERN
    # --------------------------------------------------------

    hourly = (
        filtered_df
        .groupby(
            [
                "Observation_Hour",
                "Habitat"
            ]
        )
        .size()
        .reset_index(
            name="Observations"
        )
        .sort_values(
            "Observation_Hour"
        )
    )

    fig = px.line(
        hourly,
        x="Observation_Hour",
        y="Observations",
        color="Habitat",
        markers=True,
        color_discrete_map=HABITAT_COLORS,
        title="Observation Activity by Hour"
    )

    # --------------------------------------------------------
    # SHOW VALUES ON EACH POINT
    # --------------------------------------------------------

    fig.update_traces(
        mode="lines+markers+text",

        line=dict(
            width=2.5
        ),

        marker=dict(
            size=7
        ),

        texttemplate="%{y:,}",

        textposition="top center",

        textfont=dict(
            size=9
        )
    )

    fig = style_chart(
        fig,
        height=390,
        x_title="Observation Hour",
        y_title="Observations"
    )

    fig.update_xaxes(
        dtick=1
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


    # --------------------------------------------------------
    # KEY TREND
    # --------------------------------------------------------

    if len(hourly) > 0:

        peak_row = (
            hourly
            .loc[
                hourly["Observations"].idxmax()
            ]
        )

        peak_habitat = peak_row["Habitat"]

        peak_hour = int(
            peak_row["Observation_Hour"]
        )

        peak_observations = int(
            peak_row["Observations"]
        )


        # Average observations by habitat
        habitat_avg = (
            hourly
            .groupby("Habitat")[
                "Observations"
            ]
            .mean()
            .sort_values(
                ascending=False
            )
        )


        if len(habitat_avg) >= 2:

            highest_habitat = (
                habitat_avg.index[0]
            )

            lowest_habitat = (
                habitat_avg.index[-1]
            )

            highest_avg = (
                habitat_avg.iloc[0]
            )

            lowest_avg = (
                habitat_avg.iloc[-1]
            )

            avg_difference = (
                highest_avg -
                lowest_avg
            )


            st.markdown(
                f"""
                <div style="
                    margin-top: 10px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b>
                    Observation activity peaks at
                    <b>{peak_hour}:00</b>, with
                    <b>{peak_observations:,}</b> observations
                    recorded for <b>{peak_habitat}</b>.
                    Across the observed hours,
                    <b>{highest_habitat}</b> has the higher
                    average observation activity than
                    {lowest_habitat} by approximately
                    <b>{avg_difference:,.0f}</b> observations
                    per hour.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div style="
                    margin-top: 10px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b>
                    Observation activity peaks at
                    <b>{peak_hour}:00</b>, with
                    <b>{peak_observations:,}</b> observations
                    recorded for <b>{peak_habitat}</b>.
                </div>
                """,
                unsafe_allow_html=True
            )
       # --------------------------------------------------------
    # TIME PERIOD + TEMPERATURE BAND
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # ========================================================
    # TIME PERIOD
    # ========================================================

    with col1:

        time_period = (
            filtered_df
            .groupby(
                [
                    "Time_Period",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            time_period,
            x="Time_Period",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Observations by Time Period"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            textfont=dict(
                size=10
            ),
            marker_line_width=0,

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=360,
            x_title="Time Period",
            y_title="Observations"
        )

        fig.update_layout(
            bargap=0.30,
            bargroupgap=0.08
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # TIME PERIOD KEY TREND
        # ----------------------------------------------------

        if len(time_period) > 0:

            time_totals = (
                time_period
                .groupby("Time_Period")[
                    "Observations"
                ]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            peak_period = (
                time_totals.index[0]
            )

            peak_total = int(
                time_totals.iloc[0]
            )

            peak_habitat_row = (
                time_period
                .loc[
                    time_period["Observations"].idxmax()
                ]
            )

            peak_habitat = (
                peak_habitat_row["Habitat"]
            )

            peak_habitat_value = int(
                peak_habitat_row["Observations"]
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 4px;
                    padding: 10px 13px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 13px;
                    line-height: 1.45;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{peak_period}</b> has the highest overall
                    observation activity with
                    <b>{peak_total:,}</b> observations.
                    The strongest individual habitat contribution
                    is <b>{peak_habitat}</b> with
                    <b>{peak_habitat_value:,}</b> observations.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # TEMPERATURE BAND
    # ========================================================

    with col2:

        temp_band = (
            filtered_df
            .groupby(
                [
                    "Temperature_Band",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            temp_band,
            x="Temperature_Band",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Observations by Temperature Band"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            textfont=dict(
                size=10
            ),
            marker_line_width=0,

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=360,
            x_title="Temperature Band",
            y_title="Observations"
        )

        fig.update_layout(
            bargap=0.25,
            bargroupgap=0.06
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # TEMPERATURE KEY TREND
        # ----------------------------------------------------

        if len(temp_band) > 0:

            temperature_totals = (
                temp_band
                .groupby("Temperature_Band")[
                    "Observations"
                ]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            peak_temperature = (
                temperature_totals.index[0]
            )

            peak_temperature_total = int(
                temperature_totals.iloc[0]
            )

            peak_temperature_row = (
                temp_band
                .loc[
                    temp_band["Observations"].idxmax()
                ]
            )

            peak_temperature_habitat = (
                peak_temperature_row["Habitat"]
            )

            peak_temperature_value = int(
                peak_temperature_row["Observations"]
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 4px;
                    padding: 10px 13px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 13px;
                    line-height: 1.45;
                ">
                    <b>💡 Key Trend:</b>
                    The <b>{peak_temperature}</b> temperature band
                    has the highest overall activity with
                    <b>{peak_temperature_total:,}</b> observations.
                    <b>{peak_temperature_habitat}</b> contributes the
                    most within this band with
                    <b>{peak_temperature_value:,}</b> observations.
                </div>
                """,
                unsafe_allow_html=True
            )
# ============================================================
# TAB 2 — SPECIES
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">Species Analysis</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


       # --------------------------------------------------------
    # TOP 10 SPECIES
    # --------------------------------------------------------

    with col1:

        top_species = (
            filtered_df
            .groupby("Common_Name")
            .size()
            .reset_index(
                name="Observations"
            )
            .sort_values(
                "Observations",
                ascending=False
            )
            .head(10)
            .sort_values(
                "Observations"
            )
        )

        fig = px.bar(
            top_species,
            x="Observations",
            y="Common_Name",
            orientation="h",
            text="Observations",
            title="Top 10 Most Observed Species"
        )

        fig.update_traces(
            texttemplate="%{x:,}",
            textposition="outside",
            marker_line_width=0,

            hovertemplate=(
                "<b>%{y}</b><br>"
                "Observations: %{x:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=520,
            showlegend=False,
            x_title="Observations",
            y_title=None
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY INSIGHT
        # ----------------------------------------------------

        if len(top_species) > 0:

            top_species_row = (
                top_species
                .sort_values(
                    "Observations",
                    ascending=False
                )
                .iloc[0]
            )

            top_species_name = (
                top_species_row["Common_Name"]
            )

            top_species_observations = int(
                top_species_row["Observations"]
            )

            total_top10_observations = int(
                top_species["Observations"].sum()
            )

            top10_share = (
                top_species_observations
                / total_top10_observations
                * 100
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{top_species_name}</b> is the most frequently
                    observed species with
                    <b>{top_species_observations:,}</b> observations.
                    It accounts for <b>{top10_share:.1f}%</b> of all
                    observations within the Top 10 species.
                </div>
                """,
                unsafe_allow_html=True
            )
        # --------------------------------------------------------
    # TOP SPECIES BY HABITAT
    # --------------------------------------------------------

    with col2:

        species_habitat = (
            filtered_df
            .groupby(
                [
                    "Habitat",
                    "Common_Name"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        top_names = (
            species_habitat
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby(
                "Habitat"
            )
            .head(5)
            .sort_values(
                "Observations"
            )
        )

        fig = px.bar(
            top_names,
            x="Observations",
            y="Common_Name",
            color="Habitat",
            orientation="h",
            facet_col="Habitat",
            color_discrete_map=HABITAT_COLORS,
            title="Top Species within Each Habitat"
        )

        fig.update_traces(
            marker_line_width=0,
            texttemplate="%{x:,}",
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{x:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=520,
            x_title="Observations",
            y_title=None
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND
        # ----------------------------------------------------

        if len(species_habitat) > 0:

            # Find the highest-observed species in each habitat
            habitat_top = (
                species_habitat
                .sort_values(
                    "Observations",
                    ascending=False
                )
                .groupby(
                    "Habitat"
                )
                .head(1)
            )


            trend_parts = []

            for _, row in habitat_top.iterrows():

                habitat = row["Habitat"]
                species = row["Common_Name"]
                observations = int(
                    row["Observations"]
                )

                trend_parts.append(
                    f"<b>{habitat}</b>: "
                    f"<b>{species}</b> "
                    f"({observations:,} observations)"
                )


            trend_text = " &nbsp;•&nbsp; ".join(
                trend_parts
            )


            # Find the overall strongest habitat/species combination
            overall_top = (
                species_habitat
                .sort_values(
                    "Observations",
                    ascending=False
                )
                .iloc[0]
            )

            overall_species = (
                overall_top["Common_Name"]
            )

            overall_habitat = (
                overall_top["Habitat"]
            )

            overall_observations = int(
                overall_top["Observations"]
            )


            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 14px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The most frequently observed species in each habitat
                    are: {trend_text}.
                    Overall, <b>{overall_species}</b> in
                    <b>{overall_habitat}</b> has the highest observation
                    count with <b>{overall_observations:,}</b> observations.
                </div>
                """,
                unsafe_allow_html=True
            )
    # --------------------------------------------------------
    # SPECIES KPIs
    # --------------------------------------------------------

    diversity = (
        filtered_df
        .groupby("Habitat")[
            "Scientific_Name"
        ]
        .nunique()
        .reset_index(
            name="Unique_Species"
        )
    )

    forest_species = 0
    grassland_species = 0

    if "Forest" in diversity["Habitat"].values:

        forest_species = int(
            diversity.loc[
                diversity["Habitat"] == "Forest",
                "Unique_Species"
            ].iloc[0]
        )

    if "Grassland" in diversity["Habitat"].values:

        grassland_species = int(
            diversity.loc[
                diversity["Habitat"] == "Grassland",
                "Unique_Species"
            ].iloc[0]
        )


    d1, d2, d3 = st.columns(3)

    d1.metric(
        "Total Species",
        f"{unique_species:,}"
    )

    d2.metric(
        "Forest Species",
        f"{forest_species:,}"
    )

    d3.metric(
        "Grassland Species",
        f"{grassland_species:,}"
    )


with tab2:

    # Existing Species Analysis charts
    # ...
    # --------------------------------------------------------
    # SPECIES DETAIL
    # --------------------------------------------------------

    st.markdown("### Species Detail")

    st.caption(
        "Species observation frequency within the current selection."
    )

    species_table = (
        filtered_df
        .groupby(
            [
                "Scientific_Name",
                "Common_Name"
            ]
        )
        .size()
        .reset_index(
            name="Observations"
        )
        .sort_values(
            "Observations",
            ascending=False
        )
        .reset_index(drop=True)
    )

    total_species_observations = (
        species_table["Observations"].sum()
    )

    species_table["Share"] = (
        species_table["Observations"]
        / total_species_observations
        * 100
    )

    st.dataframe(
        species_table,
        use_container_width=True,
        hide_index=True,
        height=500,

        column_config={

            "Scientific_Name": st.column_config.TextColumn(
                "Scientific Name",
                width="large"
            ),

            "Common_Name": st.column_config.TextColumn(
                "Common Name",
                width="large"
            ),

            "Observations": st.column_config.ProgressColumn(
                "Observations",
                help="Number of bird observations",
                format="%d",
                min_value=0,
                max_value=int(
                    species_table["Observations"].max()
                ),
                width="large"
            ),

            "Share": st.column_config.ProgressColumn(
                "Share",
                help="Percentage of observations",
                format="%.1f%%",
                min_value=0,
                max_value=100,
                width="medium"
            )
        }
    )


    # --------------------------------------------------------
    # KEY TREND
    # --------------------------------------------------------

    if len(species_table) > 0:

        top_species = species_table.iloc[0]

        top_species_name = (
            top_species["Common_Name"]
        )

        top_species_scientific = (
            top_species["Scientific_Name"]
        )

        top_species_observations = int(
            top_species["Observations"]
        )

        top_species_share = (
            top_species["Share"]
        )

        total_species = len(
            species_table
        )

        st.markdown(
            f"""
            <div style="
                margin-top: 12px;
                padding: 13px 16px;
                border-left: 4px solid #FF4B4B;
                border-radius: 6px;
                background: rgba(255,75,75,0.06);
                font-size: 14px;
                line-height: 1.5;
            ">
                <b>💡 Key Trend:</b>
                <b>{top_species_name}</b>
                (<i>{top_species_scientific}</i>) is the
                most frequently observed species in the current
                selection, with
                <b>{top_species_observations:,}</b> observations
                representing <b>{top_species_share:.1f}%</b>
                of all observations across
                <b>{total_species}</b> recorded species.
            </div>
            """,
            unsafe_allow_html=True
        )
# ============================================================
# TAB 3 — ENVIRONMENT & DETECTION
# ============================================================

with tab3:

    st.markdown(
        '<div class="section-title">'
        'Environmental Conditions'
        '</div>',
        unsafe_allow_html=True
    )


       # --------------------------------------------------------
    # ENVIRONMENTAL CONDITIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title"></div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # TEMPERATURE
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        fig = px.box(
            filtered_df,
            x="Habitat",
            y="Temperature",
            color="Habitat",
            points=False,
            color_discrete_map=HABITAT_COLORS,
            title="Temperature Distribution"
        )

        fig = style_chart(
            fig,
            height=400,
            x_title="Habitat",
            y_title="Temperature (°C)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # TEMPERATURE KEY TREND
        # ----------------------------------------------------

        temperature_median = (
            filtered_df
            .groupby("Habitat")["Temperature"]
            .median()
        )

        if (
            "Forest" in temperature_median.index
            and
            "Grassland" in temperature_median.index
        ):

            forest_temp = float(
                temperature_median["Forest"]
            )

            grassland_temp = float(
                temperature_median["Grassland"]
            )

            temp_difference = abs(
                forest_temp - grassland_temp
            )

            warmer_habitat = (
                "Forest"
                if forest_temp > grassland_temp
                else "Grassland"
                if grassland_temp > forest_temp
                else "both habitats"
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    Median temperature was
                    <b>{forest_temp:.1f}°C</b> in Forest and
                    <b>{grassland_temp:.1f}°C</b> in Grassland.
                    <b>{warmer_habitat}</b> had the higher median by
                    <b>{temp_difference:.1f}°C</b>.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # HUMIDITY
    # ========================================================

    with col2:

        fig = px.box(
            filtered_df,
            x="Habitat",
            y="Humidity",
            color="Habitat",
            points=False,
            color_discrete_map=HABITAT_COLORS,
            title="Humidity Distribution"
        )

        fig = style_chart(
            fig,
            height=400,
            x_title="Habitat",
            y_title="Humidity (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # HUMIDITY KEY TREND
        # ----------------------------------------------------

        humidity_median = (
            filtered_df
            .groupby("Habitat")["Humidity"]
            .median()
        )

        if (
            "Forest" in humidity_median.index
            and
            "Grassland" in humidity_median.index
        ):

            forest_humidity = float(
                humidity_median["Forest"]
            )

            grassland_humidity = float(
                humidity_median["Grassland"]
            )

            humidity_difference = abs(
                forest_humidity -
                grassland_humidity
            )

            more_humid_habitat = (
                "Forest"
                if forest_humidity > grassland_humidity
                else "Grassland"
                if grassland_humidity > forest_humidity
                else "both habitats"
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    Median humidity was
                    <b>{forest_humidity:.1f}%</b> in Forest and
                    <b>{grassland_humidity:.1f}%</b> in Grassland.
                    <b>{more_humid_habitat}</b> had the higher median by
                    <b>{humidity_difference:.1f} percentage points</b>.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # SKY CONDITIONS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        sky = (
            filtered_df
            .groupby(
                [
                    "Sky",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            sky,
            x="Sky",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            title="Sky Conditions"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=430,
            x_title="Sky Condition",
            y_title="Observations"
        )

        fig.update_xaxes(
            tickangle=-25
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # SKY KEY TREND
        # ----------------------------------------------------

        sky_top = (
            sky
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(sky_top) > 0:

            sky_insights = []

            for _, row in sky_top.iterrows():

                sky_insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['Sky']} "
                    f"({int(row['Observations']):,})"
                )

            sky_text = " &nbsp;•&nbsp; ".join(
                sky_insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The most frequently observed sky condition was
                    {sky_text}.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # WIND CONDITIONS
    # ========================================================

    with col2:

        wind = (
            filtered_df
            .groupby(
                [
                    "Wind",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            wind,
            x="Wind",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            title="Wind Conditions"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=430,
            x_title="Wind Condition",
            y_title="Observations"
        )

        fig.update_xaxes(
            tickangle=-35
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # WIND KEY TREND
        # ----------------------------------------------------

        wind_top = (
            wind
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(wind_top) > 0:

            wind_insights = []

            for _, row in wind_top.iterrows():

                wind_insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['Wind']} "
                    f"({int(row['Observations']):,})"
                )

            wind_text = " &nbsp;•&nbsp; ".join(
                wind_insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The most frequently observed wind condition was
                    {wind_text}.
                </div>
                """,
                unsafe_allow_html=True
            )
       # --------------------------------------------------------
    # DETECTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Observation & Detection'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # IDENTIFICATION METHOD
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        id_method = (
            filtered_df
            .groupby(
                [
                    "ID_Method",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            id_method,
            x="ID_Method",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Identification Method"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=420,
            x_title="Identification Method",
            y_title="Observations"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND
        # ----------------------------------------------------

        id_top = (
            id_method
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(id_top) > 0:

            insights = []

            for _, row in id_top.iterrows():

                insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['ID_Method']} "
                    f"({int(row['Observations']):,})"
                )

            insight_text = " &nbsp;•&nbsp; ".join(
                insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The dominant identification method was
                    {insight_text}.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # OBSERVATION DISTANCE
    # ========================================================

    with col2:

        distance = (
            filtered_df
            .groupby(
                [
                    "Distance",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            distance,
            x="Distance",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Observation Distance"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=420,
            x_title="Distance",
            y_title="Observations"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND
        # ----------------------------------------------------

        distance_top = (
            distance
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(distance_top) > 0:

            insights = []

            for _, row in distance_top.iterrows():

                insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['Distance']} "
                    f"({int(row['Observations']):,})"
                )

            insight_text = " &nbsp;•&nbsp; ".join(
                insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The most common observation distance was
                    {insight_text}.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # FLYOVER
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        flyover = (
            filtered_df
            .groupby(
                [
                    "Flyover_Observed",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        flyover["Flyover_Status"] = (
            flyover["Flyover_Observed"]
            .map({
                True: "Flyover",
                False: "No Flyover"
            })
        )

        fig = px.bar(
            flyover,
            x="Flyover_Status",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Flyover Observations"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=380,
            x_title=None,
            y_title="Observations"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND
        # ----------------------------------------------------

        flyover_top = (
            flyover
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(flyover_top) > 0:

            insights = []

            for _, row in flyover_top.iterrows():

                insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['Flyover_Status']} "
                    f"({int(row['Observations']):,})"
                )

            insight_text = " &nbsp;•&nbsp; ".join(
                insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    Most observations were recorded as
                    {insight_text}.
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # DISTURBANCE
    # ========================================================

    with col2:

        disturbance = (
            filtered_df
            .groupby(
                [
                    "Disturbance",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )

        fig = px.bar(
            disturbance,
            x="Disturbance",
            y="Observations",
            color="Habitat",
            barmode="group",
            color_discrete_map=HABITAT_COLORS,
            text="Observations",
            title="Disturbance During Counts"
        )

        fig.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{y:,}"
                "<extra></extra>"
            )
        )

        fig = style_chart(
            fig,
            height=380,
            x_title="Disturbance Level",
            y_title="Observations"
        )

        fig.update_xaxes(
            tickangle=-30
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND
        # ----------------------------------------------------

        disturbance_top = (
            disturbance
            .sort_values(
                "Observations",
                ascending=False
            )
            .groupby("Habitat")
            .head(1)
        )

        if len(disturbance_top) > 0:

            insights = []

            for _, row in disturbance_top.iterrows():

                insights.append(
                    f"<b>{row['Habitat']}</b>: "
                    f"{row['Disturbance']} "
                    f"({int(row['Observations']):,})"
                )

            insight_text = " &nbsp;•&nbsp; ".join(
                insights
            )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 11px 14px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 13px;
                    line-height: 1.5;
                ">
                    <b>💡 Key Trend:</b>
                    The most frequently recorded disturbance level was
                    {insight_text}.
                </div>
                """,
                unsafe_allow_html=True
            )
# ============================================================
# TAB 4 — CONSERVATION & PLOTS
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">'
        'Conservation & High-Activity Locations'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CONSERVATION KPIs
    # --------------------------------------------------------

    pif_count = len(
        filtered_df[
            filtered_df[
                "PIF_Watchlist_Status"
            ] == True
        ]
    )

    stewardship_count = len(
        filtered_df[
            filtered_df[
                "Regional_Stewardship_Status"
            ] == True
        ]
    )


    c1, c2, c3 = st.columns(3)

    c1.metric(
        "PIF Watchlist",
        f"{pif_count:,}"
    )

    c2.metric(
        "Regional Stewardship",
        f"{stewardship_count:,}"
    )

    c3.metric(
        "Conservation %",
        f"{(conservation_count / total_observations * 100):.1f}%"
    )


       # --------------------------------------------------------
    # CONSERVATION STATUS
    # --------------------------------------------------------

    conservation = pd.DataFrame({
        "Status": [
            "PIF Watchlist",
            "Regional Stewardship"
        ],
        "Observations": [
            pif_count,
            stewardship_count
        ]
    })

    # Sort so the largest category appears at the top
    conservation = (
        conservation
        .sort_values(
            "Observations",
            ascending=True
        )
    )


    # --------------------------------------------------------
    # HORIZONTAL COMPARISON CHART
    # --------------------------------------------------------

    fig = px.bar(
        conservation,
        x="Observations",
        y="Status",
        orientation="h",
        text="Observations",
        color="Status",

        color_discrete_map={
            "PIF Watchlist": "#EF4444",
            "Regional Stewardship": "#2563EB"
        },

        title="Conservation-Status Observations"
    )


    fig.update_traces(
        texttemplate="%{x:,}",
        textposition="outside",
        marker_line_width=0,

        hovertemplate=(
            "<b>%{y}</b><br>"
            "Observations: %{x:,}"
            "<extra></extra>"
        )
    )


    fig = style_chart(
        fig,
        height=300,
        showlegend=False,
        x_title="Observations",
        y_title=None
    )


    fig.update_layout(
        margin=dict(
            l=20,
            r=40,
            t=60,
            b=45
        ),

        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(100,116,139,0.10)",
            rangemode="tozero",
            tickformat=","
        ),

        yaxis=dict(
            showgrid=False
        )
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


    # --------------------------------------------------------
    # KEY TREND
    # --------------------------------------------------------

    if len(conservation) > 0:

        top_status = (
            conservation
            .sort_values(
                "Observations",
                ascending=False
            )
            .iloc[0]
        )

        lower_status = (
            conservation
            .sort_values(
                "Observations",
                ascending=True
            )
            .iloc[0]
        )

        top_value = int(
            top_status["Observations"]
        )

        lower_value = int(
            lower_status["Observations"]
        )

        difference = (
            top_value -
            lower_value
        )

        if lower_value > 0:

            ratio = (
                top_value /
                lower_value
            )

        else:

            ratio = 0


        st.markdown(
            f"""
            <div style="
                margin-top: 8px;
                padding: 12px 16px;
                border-left: 4px solid #2563EB;
                border-radius: 6px;
                background: rgba(37,99,235,0.06);
                font-size: 14px;
                line-height: 1.5;
            ">
                <b>💡 Key Trend:</b>
                <b>{top_status["Status"]}</b> recorded
                <b>{top_value:,}</b> observations compared with
                <b>{lower_value:,}</b> for
                <b>{lower_status["Status"]}</b> —
                a difference of <b>{difference:,}</b>
                observations
                ({ratio:.1f}× higher).
            </div>
            """,
            unsafe_allow_html=True
        )
        # --------------------------------------------------------
    # CONSERVATION SPECIES BY HABITAT
    # --------------------------------------------------------

    conservation_df = filtered_df[
        (
            filtered_df["PIF_Watchlist_Status"] == True
        )
        |
        (
            filtered_df["Regional_Stewardship_Status"] == True
        )
    ]


    if len(conservation_df) > 0:

        # ----------------------------------------------------
        # TOP 15 SPECIES BY TOTAL OBSERVATIONS
        # ----------------------------------------------------

        top_species = (
            conservation_df
            .groupby("Common_Name")
            .size()
            .reset_index(
                name="Total_Observations"
            )
            .sort_values(
                "Total_Observations",
                ascending=False
            )
            .head(15)
        )


        # ----------------------------------------------------
        # SPECIES + HABITAT COUNTS
        # ----------------------------------------------------

        conservation_species = (
            conservation_df
            .groupby(
                [
                    "Common_Name",
                    "Habitat"
                ]
            )
            .size()
            .reset_index(
                name="Observations"
            )
        )


        # Keep only Top 15
        conservation_species = (
            conservation_species[
                conservation_species["Common_Name"].isin(
                    top_species["Common_Name"]
                )
            ]
        )


        # ----------------------------------------------------
        # ORDER SPECIES BY TOTAL OBSERVATIONS
        # ----------------------------------------------------

        species_order = (
            top_species
            .sort_values(
                "Total_Observations",
                ascending=True
            )["Common_Name"]
            .tolist()
        )


        conservation_species["Common_Name"] = pd.Categorical(
            conservation_species["Common_Name"],
            categories=species_order,
            ordered=True
        )


        # ----------------------------------------------------
        # HABITAT COLORS
        # ----------------------------------------------------

        habitat_colors = {
            "Forest": "#2563EB",
            "Grassland": "#16A34A"
        }


        # ----------------------------------------------------
        # STACKED HORIZONTAL BAR
        # ----------------------------------------------------

        fig = px.bar(
            conservation_species,
            x="Observations",
            y="Common_Name",
            color="Habitat",
            orientation="h",
            barmode="stack",
            color_discrete_map=habitat_colors,
            category_orders={
                "Common_Name": species_order,
                "Habitat": [
                    "Forest",
                    "Grassland"
                ]
            },
            title="Top Conservation-Status Species by Habitat",
            custom_data=[
                "Habitat"
            ]
        )


        # ----------------------------------------------------
        # BAR STYLING
        # ----------------------------------------------------

        fig.update_traces(
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Habitat: %{customdata[0]}<br>"
                "Observations: %{x:,}"
                "<extra></extra>"
            )
        )


        # ----------------------------------------------------
        # CHART LAYOUT
        # ----------------------------------------------------

        fig.update_layout(

            height=540,

            margin=dict(
                l=10,
                r=35,
                t=90,
                b=45
            ),

            title=dict(
                text="Top Conservation-Status Species by Habitat",
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
                font=dict(
                    size=18
                )
            ),

            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="right",
                x=1
            ),

            xaxis=dict(
                title="Total Observations",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.18)",
                zeroline=False
            ),

            yaxis=dict(
                title=None,
                showgrid=False,
                categoryorder="array",
                categoryarray=species_order
            ),

            bargap=0.28,

            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )


        # ----------------------------------------------------
        # TOTAL LABELS
        # ----------------------------------------------------

        totals_for_labels = (
            top_species
            .copy()
            .sort_values(
                "Total_Observations",
                ascending=True
            )
        )


        for _, row in totals_for_labels.iterrows():

            fig.add_annotation(
                x=row["Total_Observations"],
                y=row["Common_Name"],
                text=f"{int(row['Total_Observations']):,}",
                showarrow=False,
                xanchor="left",
                xshift=7,
                font=dict(
                    size=10
                )
            )


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND - CONSERVATION SPECIES
        # ----------------------------------------------------

        if len(top_species) > 0:

            top_conservation = (
                top_species
                .sort_values(
                    "Total_Observations",
                    ascending=False
                )
                .iloc[0]
            )

            top_species_name = (
                top_conservation["Common_Name"]
            )

            top_species_count = int(
                top_conservation["Total_Observations"]
            )

            habitat_breakdown = (
                conservation_species[
                    conservation_species["Common_Name"]
                    == top_species_name
                ]
                .sort_values(
                    "Observations",
                    ascending=False
                )
            )

            if len(habitat_breakdown) > 0:

                leading_habitat = (
                    habitat_breakdown.iloc[0]["Habitat"]
                )

                leading_habitat_count = int(
                    habitat_breakdown.iloc[0]["Observations"]
                )

                habitat_share = (
                    leading_habitat_count
                    / top_species_count
                    * 100
                )

                trend_text = (
                    f"<b>{top_species_name}</b> is the most observed "
                    f"conservation-status species with "
                    f"<b>{top_species_count:,}</b> observations. "
                    f"<b>{leading_habitat}</b> contributes "
                    f"<b>{leading_habitat_count:,}</b> "
                    f"({habitat_share:.1f}%) of its observations."
                )

            else:

                trend_text = (
                    f"<b>{top_species_name}</b> leads the "
                    f"conservation-status species with "
                    f"<b>{top_species_count:,}</b> observations."
                )

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b> {trend_text}
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # PLOT ACTIVITY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Plot-Level Activity</div>',
        unsafe_allow_html=True
    )

    plot_activity = (
        filtered_df
        .groupby(
            [
                "Habitat",
                "Plot_Name"
            ]
        )
        .size()
        .reset_index(
            name="Observations"
        )
        .sort_values(
            "Observations",
            ascending=False
        )
    )


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # TOP 15 MOST ACTIVE PLOTS — EACH HABITAT
    # --------------------------------------------------------

    with col1:

        # Top 15 Forest plots
        forest_plots = (
            plot_activity[
                plot_activity["Habitat"] == "Forest"
            ]
            .sort_values(
                "Observations",
                ascending=False
            )
            .head(15)
        )


        # Top 15 Grassland plots
        grassland_plots = (
            plot_activity[
                plot_activity["Habitat"] == "Grassland"
            ]
            .sort_values(
                "Observations",
                ascending=False
            )
            .head(15)
        )


        # Combine both rankings
        top_plots = pd.concat(
            [
                forest_plots,
                grassland_plots
            ],
            ignore_index=True
        )


        # Sort so highest activity appears at the top
        top_plots = (
            top_plots
            .sort_values(
                "Observations",
                ascending=True
            )
        )


        # ----------------------------------------------------
        # SECTION TITLE
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                font-size: 22px;
                font-weight: 700;
                margin: 10px 0 15px 0;
            ">
                Top 15 Most Active Plots by Habitat
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        fig = px.bar(
            top_plots,
            x="Observations",
            y="Plot_Name",
            color="Habitat",
            orientation="h",
            text="Observations",
            color_discrete_map={
                "Forest": "#2563EB",
                "Grassland": "#16A34A"
            },
            category_orders={
                "Habitat": [
                    "Forest",
                    "Grassland"
                ]
            }
        )


        # ----------------------------------------------------
        # BAR FORMATTING
        # ----------------------------------------------------

        fig.update_traces(
            textposition="outside",
            textfont=dict(
                size=10
            ),
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Habitat: %{fullData.name}<br>"
                "Observations: %{x:,}"
                "<extra></extra>"
            )
        )


        # ----------------------------------------------------
        # CHART LAYOUT
        # ----------------------------------------------------

        fig.update_layout(
            height=700,

            margin=dict(
                l=10,
                r=45,
                t=25,
                b=50
            ),

            title=None,

            legend=dict(
                title=None,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),

            xaxis=dict(
                title="Observations",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.18)",
                zeroline=False
            ),

            yaxis=dict(
                title=None,
                showgrid=False
            ),

            bargap=0.22,

            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ----------------------------------------------------
        # KEY TREND - MOST ACTIVE PLOTS
        # ----------------------------------------------------

        if len(top_plots) > 0:

            most_active_plot = (
                top_plots
                .sort_values(
                    "Observations",
                    ascending=False
                )
                .iloc[0]
            )

            forest_top = (
                forest_plots["Observations"].max()
                if len(forest_plots) > 0
                else None
            )

            grassland_top = (
                grassland_plots["Observations"].max()
                if len(grassland_plots) > 0
                else None
            )

            if (
                forest_top is not None
                and grassland_top is not None
            ):

                if grassland_top > forest_top:

                    habitat_comparison = (
                        f"Grassland's most active plot recorded "
                        f"<b>{int(grassland_top):,}</b> observations "
                        f"versus <b>{int(forest_top):,}</b> for Forest."
                    )

                elif forest_top > grassland_top:

                    habitat_comparison = (
                        f"Forest's most active plot recorded "
                        f"<b>{int(forest_top):,}</b> observations "
                        f"versus <b>{int(grassland_top):,}</b> for Grassland."
                    )

                else:

                    habitat_comparison = (
                        "The most active Forest and Grassland plots "
                        "recorded the same number of observations."
                    )

            else:

                habitat_comparison = ""

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{most_active_plot["Plot_Name"]}</b> is the most
                    active plot with
                    <b>{int(most_active_plot["Observations"]):,}</b>
                    observations and belongs to the
                    <b>{most_active_plot["Habitat"]}</b> habitat.
                    {habitat_comparison}
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # PLOT SUMMARY
    # --------------------------------------------------------

    with col2:

        plot_summary = (
            plot_activity
            .groupby("Habitat")[
                "Observations"
            ]
            .agg(
                Number_of_Plots="count",
                Mean_Observations="mean",
                Median_Observations="median",
                Maximum_Observations="max"
            )
            .reset_index()
        )


        plot_summary[
            "Mean_Observations"
        ] = plot_summary[
            "Mean_Observations"
        ].round(2)


        plot_summary[
            "Median_Observations"
        ] = plot_summary[
            "Median_Observations"
        ].round(2)


        st.markdown(
            "### Plot Performance"
        )


        st.dataframe(
    plot_summary,
    use_container_width=True,
    hide_index=True,
    column_config={

        "Habitat": st.column_config.TextColumn(
            "Habitat"
        ),

        "Number_of_Plots": st.column_config.NumberColumn(
            "Number of Plots",
            format="%d"
        ),

        "Mean_Observations": st.column_config.NumberColumn(
            "Mean Observations",
            format="%.2f"
        ),

        "Median_Observations": st.column_config.NumberColumn(
            "Median Observations",
            format="%.0f"
        ),

        "Maximum_Observations": st.column_config.NumberColumn(
            "Maximum Observations",
            format="%d"
        )
    }
)

        # ----------------------------------------------------
        # KEY TREND - PLOT PERFORMANCE
        # ----------------------------------------------------

        if len(plot_summary) > 0:

            best_average_habitat = (
                plot_summary
                .sort_values(
                    "Mean_Observations",
                    ascending=False
                )
                .iloc[0]
            )

            lowest_average_habitat = (
                plot_summary
                .sort_values(
                    "Mean_Observations",
                    ascending=True
                )
                .iloc[0]
            )

            mean_difference = (
                best_average_habitat["Mean_Observations"]
                - lowest_average_habitat["Mean_Observations"]
            )

            if (
                lowest_average_habitat["Mean_Observations"]
                > 0
            ):

                mean_difference_pct = (
                    mean_difference
                    / lowest_average_habitat["Mean_Observations"]
                    * 100
                )

            else:

                mean_difference_pct = 0

            st.markdown(
                f"""
                <div style="
                    margin-top: 8px;
                    padding: 12px 16px;
                    border-left: 4px solid #2563EB;
                    border-radius: 6px;
                    background: rgba(37,99,235,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{best_average_habitat["Habitat"]}</b> plots have
                    the highest average activity at
                    <b>{best_average_habitat["Mean_Observations"]:.2f}</b>
                    observations per plot — approximately
                    <b>{mean_difference_pct:.1f}% higher</b> than
                    {lowest_average_habitat["Habitat"]}.
                </div>
                """,
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # HIGHEST ACTIVITY PLOT
        # ----------------------------------------------------

        if len(plot_activity) > 0:

            top_plot = (
                plot_activity
                .sort_values(
                    "Observations",
                    ascending=False
                )
                .iloc[0]
            )


            st.markdown(
                "### Highest Activity Plot"
            )


            st.metric(
                "Plot",
                top_plot["Plot_Name"]
            )


            st.metric(
                "Observations",
                f"{int(top_plot['Observations']):,}"
            )


            st.caption(
                f"Habitat: {top_plot['Habitat']}"
            )


            # ------------------------------------------------
            # KEY TREND - HIGHEST ACTIVITY PLOT
            # ------------------------------------------------

            total_plot_observations = (
                plot_activity["Observations"].sum()
            )

            if total_plot_observations > 0:

                top_plot_share = (
                    top_plot["Observations"]
                    / total_plot_observations
                    * 100
                )

            else:

                top_plot_share = 0

            st.markdown(
                f"""
                <div style="
                    margin-top: 10px;
                    padding: 12px 16px;
                    border-left: 4px solid #16A34A;
                    border-radius: 6px;
                    background: rgba(22,163,74,0.06);
                    font-size: 14px;
                ">
                    <b>💡 Key Trend:</b>
                    <b>{top_plot["Plot_Name"]}</b> has the highest
                    activity with
                    <b>{int(top_plot["Observations"]):,}</b>
                    observations, representing
                    <b>{top_plot_share:.1f}%</b> of all plot-level
                    observations in the current selection.
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # PLOT DETAIL
    # --------------------------------------------------------

    st.markdown(
        "### Plot Activity Detail"
    )


    st.dataframe(
        plot_activity,
        use_container_width=True,
        hide_index=True,
        height=350
    )


    # --------------------------------------------------------
    # KEY TREND - PLOT ACTIVITY DETAIL
    # --------------------------------------------------------

    if len(plot_activity) > 0:

        highest_plot = (
            plot_activity
            .sort_values(
                "Observations",
                ascending=False
            )
            .iloc[0]
        )

        lowest_plot = (
            plot_activity
            .sort_values(
                "Observations",
                ascending=True
            )
            .iloc[0]
        )

        st.markdown(
            f"""
            <div style="
                margin-top: 8px;
                padding: 12px 16px;
                border-left: 4px solid #64748B;
                border-radius: 6px;
                background: rgba(100,116,139,0.06);
                font-size: 14px;
            ">
                <b>💡 Key Trend:</b>
                Plot activity ranges from
                <b>{int(lowest_plot["Observations"]):,}</b> to
                <b>{int(highest_plot["Observations"]):,}</b>
                observations.
                <b>{highest_plot["Plot_Name"]}</b> records the highest
                activity, while
                <b>{lowest_plot["Plot_Name"]}</b> records the lowest.
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # FILTERED OBSERVATION DATA
    # --------------------------------------------------------

    st.markdown(
        "### Filtered Observation Data"
    )


    st.caption(
        "Select a row to inspect the complete observation details."
    )


    display_columns = [
        "Date",
        "Habitat",
        "Plot_Name",
        "Common_Name",
        "Scientific_Name",
        "Observation_Hour",
        "Temperature",
        "Humidity",
        "ID_Method",
        "Distance",
        "PIF_Watchlist_Status",
        "Regional_Stewardship_Status"
    ]


    display_columns = [
        col
        for col in display_columns
        if col in filtered_df.columns
    ]


    filtered_table = (
        filtered_df[
            display_columns
        ]
        .sort_values(
            "Date",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # KEEP ORIGINAL STATUS VALUES FOR SELECTION
    # --------------------------------------------------------

    table_display = filtered_table.copy()


    # --------------------------------------------------------
    # VISUAL STATUS DOTS
    # --------------------------------------------------------

    table_display["PIF_Watchlist_Status"] = (
        table_display[
            "PIF_Watchlist_Status"
        ]
        .map({
            True: "🔴",
            False: "⚪"
        })
    )


    table_display["Regional_Stewardship_Status"] = (
        table_display[
            "Regional_Stewardship_Status"
        ]
        .map({
            True: "🔴",
            False: "⚪"
        })
    )


    # --------------------------------------------------------
    # INTERACTIVE TABLE
    # --------------------------------------------------------

    selected_rows = st.dataframe(
        table_display,

        use_container_width=True,

        hide_index=True,

        height=420,

        on_select="rerun",

        selection_mode="single-row",

        column_config={

            "Date": st.column_config.DatetimeColumn(
                "Date",
                format="DD MMM YYYY",
                width="medium"
            ),

            "Habitat": st.column_config.TextColumn(
                "Habitat",
                width="small"
            ),

            "Plot_Name": st.column_config.TextColumn(
                "Plot",
                width="small"
            ),

            "Common_Name": st.column_config.TextColumn(
                "Common Name",
                width="medium"
            ),

            "Scientific_Name": st.column_config.TextColumn(
                "Scientific Name",
                width="medium"
            ),

            "Observation_Hour": st.column_config.NumberColumn(
                "Hour",
                format="%d",
                width="small"
            ),

            "Temperature": st.column_config.NumberColumn(
                "Temperature °C",
                format="%.1f",
                width="small"
            ),

            "Humidity": st.column_config.NumberColumn(
                "Humidity %",
                format="%.1f",
                width="small"
            ),

            "ID_Method": st.column_config.TextColumn(
                "ID Method",
                width="medium"
            ),

            "Distance": st.column_config.TextColumn(
                "Distance",
                width="medium"
            ),

            "PIF_Watchlist_Status": st.column_config.TextColumn(
                "PIF Watchlist",
                help="🔴 Listed on PIF Watchlist | ⚪ Not listed",
                width="small"
            ),

            "Regional_Stewardship_Status": st.column_config.TextColumn(
                "Regional Stewardship",
                help="🔴 Regional Stewardship | ⚪ Not listed",
                width="small"
            )
        }
    )


    # --------------------------------------------------------
    # KEY TREND - FILTERED OBSERVATION DATA
    # --------------------------------------------------------

    if len(filtered_table) > 0:

        filtered_total = len(filtered_table)


        # ----------------------------------------------------
        # DOMINANT HABITAT
        # ----------------------------------------------------

        habitat_counts_filtered = (
            filtered_table["Habitat"]
            .value_counts()
        )

        dominant_habitat = (
            habitat_counts_filtered.index[0]
        )

        dominant_habitat_count = int(
            habitat_counts_filtered.iloc[0]
        )

        dominant_habitat_share = (
            dominant_habitat_count
            / filtered_total
            * 100
        )


        # ----------------------------------------------------
        # MOST OBSERVED SPECIES
        # ----------------------------------------------------

        species_counts_filtered = (
            filtered_table["Common_Name"]
            .value_counts()
        )

        dominant_species = (
            species_counts_filtered.index[0]
        )

        dominant_species_count = int(
            species_counts_filtered.iloc[0]
        )


        # ----------------------------------------------------
        # MOST COMMON ID METHOD
        # ----------------------------------------------------

        id_counts_filtered = (
            filtered_table["ID_Method"]
            .value_counts()
        )

        dominant_id_method = (
            id_counts_filtered.index[0]
        )

        dominant_id_count = int(
            id_counts_filtered.iloc[0]
        )


        st.markdown(
            f"""
            <div style="
                margin-top: 10px;
                padding: 12px 16px;
                border-left: 4px solid #2563EB;
                border-radius: 6px;
                background: rgba(37,99,235,0.06);
                font-size: 14px;
            ">
                <b>💡 Key Trend:</b>
                The current selection contains
                <b>{filtered_total:,}</b> observations.
                <b>{dominant_habitat}</b> is the dominant habitat with
                <b>{dominant_habitat_count:,}</b> observations
                ({dominant_habitat_share:.1f}%).
                The most frequently observed species is
                <b>{dominant_species}</b>
                ({dominant_species_count:,} observations), while
                <b>{dominant_id_method}</b> is the most common
                identification method
                ({dominant_id_count:,} observations).
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # SELECTED OBSERVATION
    # --------------------------------------------------------

    if selected_rows.selection.rows:

        selected_index = (
            selected_rows.selection.rows[0]
        )


        selected_observation = (
            filtered_table
            .iloc[selected_index]
        )


        st.markdown(
            "#### 🔎 Selected Observation"
        )


        d1, d2, d3, d4 = st.columns(4)


        with d1:

            st.metric(
                "Species",
                selected_observation["Common_Name"]
            )


        with d2:

            st.metric(
                "Habitat",
                selected_observation["Habitat"]
            )


        with d3:

            st.metric(
                "Plot",
                selected_observation["Plot_Name"]
            )


        with d4:

            st.metric(
                "ID Method",
                selected_observation["ID_Method"]
            )


        st.markdown(
            "##### Observation Details"
        )


        detail_col1, detail_col2 = st.columns(2)


        with detail_col1:

            st.write(
                f"**Scientific Name:** "
                f"{selected_observation['Scientific_Name']}"
            )

            st.write(
                f"**Date:** "
                f"{selected_observation['Date'].strftime('%d %B %Y')}"
            )

            st.write(
                f"**Observation Hour:** "
                f"{selected_observation['Observation_Hour']}"
            )

            st.write(
                f"**Distance:** "
                f"{selected_observation['Distance']}"
            )


        with detail_col2:

            st.write(
                f"**Temperature:** "
                f"{selected_observation['Temperature']:.1f} °C"
            )

            st.write(
                f"**Humidity:** "
                f"{selected_observation['Humidity']:.1f}%"
            )

            st.write(
                f"**PIF Watchlist:** "
                f"{'🔴 Yes' if selected_observation['PIF_Watchlist_Status'] else '⚪ No'}"
            )

            st.write(
                f"**Regional Stewardship:** "
                f"{'🔴 Yes' if selected_observation['Regional_Stewardship_Status'] else '⚪ No'}"
            )


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        csv_data = (
            filtered_df
            .to_csv(index=False)
            .encode("utf-8")
        )


        st.download_button(
            label="⬇️ Download Filtered Data",
            data=csv_data,
            file_name="filtered_bird_observations.csv",
            mime="text/csv"
        )
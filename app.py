import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(page_title="Food Delivery Dashboard", page_icon="🍔", layout="wide")


# =========================================================
# DARK THEME
# =========================================================

st.markdown(
    """
<style>

.block-container {
    max-width: 1600px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.stApp {
    background-color: #080D16;
}

[data-testid="stMetric"] {
    background-color: #111A2A;
    border: 1px solid #1F3048;
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stMetricValue"] {
    font-size: 28px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# COLORS
# =========================================================

DARK_COLORS = ["#304B78", "#51346F", "#355C4A", "#6D63A8", "#713B52", "#5C461F"]

TRAFFIC_COLORS = {
    "Low": "#355C4A",
    "Medium": "#6D63A8",
    "High": "#304B78",
    "Jam": "#713B52",
    "Unknown": "#5C461F",
}


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("food_delivery_final.csv")


# =========================================================
# DATA TYPES
# =========================================================

if "Order_Date" in df.columns:

    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")


# =========================================================
# CREATE DISTANCE COLUMN IF NOT FOUND
# =========================================================

if "Delivery_Distance_km" not in df.columns:

    coord_cols = [
        "Restaurant_latitude",
        "Restaurant_longitude",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
    ]

    if all(col in df.columns for col in coord_cols):

        R = 6371

        lat1 = np.radians(df["Restaurant_latitude"])

        lon1 = np.radians(df["Restaurant_longitude"])

        lat2 = np.radians(df["Delivery_location_latitude"])

        lon2 = np.radians(df["Delivery_location_longitude"])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2

        df["Delivery_Distance_km"] = 2 * R * np.arcsin(np.sqrt(a))


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.image("delivery.png", width=150)
st.sidebar.markdown("🔽 Filters")


# -------------------------
# CITY
# -------------------------

city_options = ["All"] + sorted(df["City"].dropna().astype(str).unique().tolist())

selected_city = st.sidebar.selectbox("🏙️ City", city_options)


# -------------------------
# TRAFFIC
# -------------------------

traffic_options = ["All"] + sorted(
    df["Road_traffic_density"].dropna().astype(str).unique().tolist()
)

selected_traffic = st.sidebar.selectbox("🚦 Traffic Density", traffic_options)


# -------------------------
# VEHICLE
# -------------------------

vehicle_options = ["All"] + sorted(
    df["Type_of_vehicle"].dropna().astype(str).unique().tolist()
)

selected_vehicle = st.sidebar.selectbox("🚚 Vehicle", vehicle_options)


# -------------------------
# WEATHER
# -------------------------

weather_options = ["All"] + sorted(
    df["Weatherconditions"].dropna().astype(str).unique().tolist()
)

selected_weather = st.sidebar.selectbox("🌤️ Weather", weather_options)


# -------------------------
# ORDER TYPE
# -------------------------

order_options = ["All"] + sorted(
    df["Type_of_order"].dropna().astype(str).unique().tolist()
)

selected_order = st.sidebar.selectbox("🍽️ Order Type", order_options)


# -------------------------
# DATE
# -------------------------

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

order_date_range = st.sidebar.slider(
    "📅 Order Date", min_value=min_date, max_value=max_date, value=(min_date, max_date)
)


# -------------------------
# DELIVERY TIME
# -------------------------

min_time = int(df["Time_taken(min)"].min())

max_time = int(df["Time_taken(min)"].max())

delivery_time_range = st.sidebar.slider(
    "⏱️ Delivery Time",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
)


# -------------------------
# AGE
# -------------------------

min_age = int(df["Delivery_person_Age"].min())

max_age = int(df["Delivery_person_Age"].max())

age_range = st.sidebar.slider(
    "👤 Delivery Person Age",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age),
)


# -------------------------
# FESTIVAL
# -------------------------

festival_options = ["All"] + sorted(
    df["Festival"].dropna().astype(str).unique().tolist()
)

selected_festival = st.sidebar.selectbox("🎉 Festival", festival_options)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_city != "All":

    filtered_df = filtered_df[filtered_df["City"].astype(str) == selected_city]


if selected_traffic != "All":

    filtered_df = filtered_df[
        filtered_df["Road_traffic_density"].astype(str) == selected_traffic
    ]


if selected_vehicle != "All":

    filtered_df = filtered_df[
        filtered_df["Type_of_vehicle"].astype(str) == selected_vehicle
    ]


if selected_weather != "All":

    filtered_df = filtered_df[
        filtered_df["Weatherconditions"].astype(str) == selected_weather
    ]


if selected_order != "All":

    filtered_df = filtered_df[
        filtered_df["Type_of_order"].astype(str) == selected_order
    ]


filtered_df = filtered_df[
    filtered_df["Order_Date"].dt.date.between(order_date_range[0], order_date_range[1])
]


filtered_df = filtered_df[
    filtered_df["Time_taken(min)"].between(
        delivery_time_range[0], delivery_time_range[1]
    )
]


filtered_df = filtered_df[
    filtered_df["Delivery_person_Age"].between(age_range[0], age_range[1])
]


if selected_festival != "All":

    filtered_df = filtered_df[filtered_df["Festival"].astype(str) == selected_festival]


# =========================================================
# HEADER
# =========================================================

st.title("🍔 Dashboard Food Delivery")

st.markdown("## Performance Overview")


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📊 Overview",
        "📊 Overview Time",
        "🚚 Delivery Analysis",
        "📈 Trends & Relationships",
        "🌦️ Weather & Traffic",
        "🏆 Delivery Persons",
        "💡 Insights & Relationships",
    ]
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

# Total Orders
total_orders = len(filtered_df)

# Average Delivery Time
avg_delivery_time = filtered_df["Time_taken(min)"].mean()

# Number of Delivery Persons
delivery_persons = filtered_df["Delivery_person_ID"].nunique()


# =========================================================
# PEAK ORDER TIME
# =========================================================

possible_time_columns = ["Time_orderd", "Time_Orderd", "Time_Order", "Time_order"]

time_col = next(
    (col for col in possible_time_columns if col in filtered_df.columns), None
)

if time_col:

    order_time = pd.to_datetime(
        filtered_df[time_col].astype(str), errors="coerce", format="mixed"
    )

    hour_counts = order_time.dt.hour.value_counts()

    if not hour_counts.empty:

        peak_hour = hour_counts.idxmax()

        next_hour = (peak_hour + 1) % 24

        peak_order_time = f"{peak_hour:02d}:00 - {next_hour:02d}:00"

    else:
        peak_order_time = "N/A"

else:
    peak_order_time = "N/A"
# =========================================================
# TAB 1 - OVERVIEW
# =========================================================

with tab1:

    st.header("📊 Overview")

    # =====================================================
    # KPI CARDS
    # =====================================================

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric("📦 Total Orders", f"{total_orders:,}")

    with kpi2:
        st.metric("⏱️ Avg Delivery Time", f"{avg_delivery_time:.1f} min")

    with kpi3:
        st.metric("🔥 Peak Order Time", peak_order_time)

    with kpi4:
        st.metric("👥 Delivery Persons", f"{delivery_persons:,}")

    st.markdown("---")

    # =====================================================
    # ROW - 3 CHARTS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    # -----------------------------------------------------
    # 1. ORDERS BY DELIVERY DISTANCE
    # -----------------------------------------------------

    with col1:

        distance_category = pd.cut(
            filtered_df["Delivery_Distance_km"],
            bins=[-np.inf, 12, np.inf],
            labels=["Near (<12 km)", "Far (≥12 km)"],
        )

        distance_counts = (
            distance_category.value_counts()
            .reindex(["Near (<12 km)", "Far (≥12 km)"], fill_value=0)
            .reset_index()
        )

        distance_counts.columns = ["Distance Category", "Orders"]

        fig_distance = px.pie(
            distance_counts,
            names="Distance Category",
            values="Orders",
            hole=0.55,
            title="Orders by Delivery Distance",
        )

        fig_distance.update_traces(
            texttemplate="%{percent:.1%}",
            textposition="inside",
            hovertemplate=(
                "<b>Distance:</b> %{label}"
                "<br><b>Orders:</b> %{value:,}"
                "<br><b>Percentage:</b> %{percent:.1%}"
                "<extra></extra>"
            ),
        )

        fig_distance.update_layout(
            height=320,
            margin=dict(t=55, b=20, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            showlegend=True,
            legend=dict(orientation="h", y=-0.05),
            annotations=[
                dict(
                    text=f"<b>{total_orders:,}</b><br>Total Orders",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="white"),
                )
            ],
        )

        st.plotly_chart(fig_distance, width="stretch", key="overview_delivery_distance")

    # -----------------------------------------------------
    # 2. ORDERS TREND OVER TIME
    # -----------------------------------------------------

    with col3:

        trend_data = filtered_df.groupby("Order_Date").size().reset_index(name="Orders")

        fig_trend = px.line(
            trend_data,
            x="Order_Date",
            y="Orders",
            title="Orders Trend Over Time",
            labels={"Order_Date": "Order_Date", "Orders": "Orders"},
        )

        fig_trend.update_traces(
            line=dict(color="#8FA8FF", width=3),
            hovertemplate=(
                "<b>Date:</b> %{x|%b %d, %Y}"
                "<br><b>Orders:</b> %{y:,}"
                "<extra></extra>"
            ),
        )

        fig_trend.update_layout(
            height=320,
            margin=dict(t=55, b=40, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Order_Date",
            yaxis_title="Orders",
        )

        st.plotly_chart(fig_trend, width="stretch", key="overview_orders_trend")

    # -----------------------------------------------------
    # 3. ORDERS BY TYPE
    # -----------------------------------------------------

    with col2:

        order_type = filtered_df["Type_of_order"].value_counts().reset_index()

        order_type.columns = ["Order Type", "Orders"]

        fig_type = px.bar(
            order_type,
            x="Orders",
            y="Order Type",
            orientation="h",
            title="Orders by Type",
            text="Orders",
        )

        fig_type.update_traces(
            marker_color=["#315A86", "#5B3F8C", "#4A7896", "#8A4F5F"],
            texttemplate="%{x:,}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>Order Type:</b> %{y}" "<br><b>Orders:</b> %{x:,}" "<extra></extra>"
            ),
        )

        fig_type.update_layout(
            height=320,
            margin=dict(t=55, b=40, l=10, r=60),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Orders",
            yaxis_title="Order Type",
            xaxis=dict(range=[0, order_type["Orders"].max() * 1.20]),
        )

        st.plotly_chart(fig_type, width="stretch", key="overview_orders_by_type")

    # -----------------------------------------------------
    # 4 — ORDERS BY TYPE
    # -----------------------------------------------------
with tab2:

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric("📦 Total Orders", f"{total_orders:,}")

    with kpi2:

        st.metric("⏱️ Avg Delivery Time", f"{avg_delivery_time:.1f} min")

    with kpi3:

        st.metric("🔥 Peak Order Time", peak_order_time)

    with kpi4:

        st.metric("🚴 Delivery Persons", f"{delivery_persons:,}")

    st.markdown("")

    col1, col2, col3 = st.columns(3)

    with col1:
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        weekday_orders = (
            filtered_df.assign(Day=filtered_df["Order_Date"].dt.day_name())
            .groupby("Day")
            .size()
            .reindex(weekday_order, fill_value=0)
            .reset_index(name="Orders")
        )

        fig_weekday = px.bar(
            weekday_orders,
            x="Day",
            y="Orders",
            title="Orders by Day of Week",
            text="Orders",
            color="Day",
            color_discrete_sequence=[
                "#304B78",
                "#51346F",
                "#355C4A",
                "#6D63A8",
                "#713B52",
                "#5C461F",
                "#8FA8FF",
            ],
        )

        fig_weekday.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>Day:</b> %{x}" "<br><b>Orders:</b> %{y:,}" "<extra></extra>"
            ),
        )

        fig_weekday.update_layout(height=350, margin=dict(t=55, b=10, l=10, r=10))

        st.plotly_chart(fig_weekday, width="stretch")

    # -----------------------------------------------------
    # 3 — BEFORE / AFTER 12 PM
    # -----------------------------------------------------

    with col2:

        time_columns = ["Time_orderd", "Time_Orderd", "Time_Order", "Time_order"]

        time_col = next(
            (col for col in time_columns if col in filtered_df.columns), None
        )

        if time_col:

            order_time = pd.to_datetime(
                filtered_df[time_col].astype(str), errors="coerce"
            )

        before_after = pd.Series(
            {
                "1 AM - 12 PM": (order_time.dt.hour < 13).sum(),
                "1 PM - 12 AM": (order_time.dt.hour >= 13).sum(),
            }
        )

        time_df = before_after.reset_index()

        time_df.columns = ["Time Period", "Orders"]

        fig_time = px.pie(
            time_df,
            names="Time Period",
            values="Orders",
            hole=0.65,
            title="Orders Before and After 12 PM",
            color="Time Period",
            color_discrete_map={
                "1 PM - 12 AM": "#304B78",
                "1 AM - 12 PM": "#6FAFA6",
            },
        )

        fig_time.update_traces(
            texttemplate="%{percent:.1%}",
            textposition="inside",
            hovertemplate=(
                "<b>%{label}</b>"
                "<br><b>Orders:</b> %{value:,}"
                "<br><b>Percentage:</b> %{percent:.1%}"
                "<extra></extra>"
            ),
        )

        fig_time.update_layout(height=350, margin=dict(t=55, b=10, l=10, r=10))

        st.plotly_chart(fig_time, width="stretch")

        st.empty()

    with col3:
        # ========================================================
        # 6 - ORDERS BY TIME OF DAY
        # ========================================================

        time_data = filtered_df.copy()

        # Detect time column
        possible_time_columns = [
            "Time_orderd",
            "Time_Orderd",
            "Time_Order",
            "Time_order",
        ]

        time_col = next(
            (col for col in possible_time_columns if col in time_data.columns), None
        )

        if time_col is not None:

            # Convert order time to datetime
            time_data["Order_Hour"] = pd.to_datetime(
                time_data[time_col], errors="coerce"
            ).dt.hour

        # 2-hour intervals
        bins = list(range(0, 25, 2))

        labels = [
            "12 AM - 2 AM",
            "2 AM - 4 AM",
            "4 AM - 6 AM",
            "6 AM - 8 AM",
            "8 AM - 10 AM",
            "10 AM - 12 PM",
            "12 PM - 2 PM",
            "2 PM - 4 PM",
            "4 PM - 6 PM",
            "6 PM - 8 PM",
            "8 PM - 10 PM",
            "10 PM - 12 AM",
        ]

        time_data["Time Period"] = pd.cut(
            time_data["Order_Hour"],
            bins=bins,
            labels=labels,
            right=False,
            include_lowest=True,
        )

        orders_by_time = (
            time_data["Time Period"]
            .value_counts()
            .reindex(labels, fill_value=0)
            .reset_index()
        )

        orders_by_time.columns = ["Time Period", "Orders"]

        # Different dark colors
        TIME_COLORS = [
            "#315A86",
            "#4A7896",
            "#5B3F8C",
            "#6A4C93",
            "#784F7A",
            "#8A4F5F",
            "#934B5F",
            "#7A3E55",
            "#5B3F8C",
            "#315A86",
            "#4A7896",
            "#6B527F",
        ]

        fig_time_orders = px.bar(
            orders_by_time,
            x="Time Period",
            y="Orders",
            title="Orders by Time of Day",
            text="Orders",
        )

        fig_time_orders.update_traces(
            marker_color=TIME_COLORS,
            texttemplate="%{y:,}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>Time:</b> %{x}" "<br><b>Orders:</b> %{y:,}" "<extra></extra>"
            ),
        )

        fig_time_orders.update_layout(
            height=300,
            margin=dict(t=50, b=45, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(title="Time of Day", tickangle=-45),
            yaxis=dict(
                title="Orders", range=[0, orders_by_time["Orders"].max() * 1.20]
            ),
        )

        st.plotly_chart(fig_time_orders, width="stretch", key="overview_orders_by_time")


# ============================================================
# TAB 3 - DELIVERY ANALYSIS
# ============================================================

with tab3:

    st.header("🚚 Delivery Analysis")

    # ========================================================
    # DARK COLORS
    # ========================================================

    CITY_COLORS = [
        "#315A86",  # Dark Blue
        "#5B3F8C",  # Dark Purple
        "#8A4F5F",  # Burgundy
        "#4A7896",  # Dark Cyan
    ]

    CITY_ORDER_COLORS = ["#315A86", "#5B3F8C", "#8A4F5F", "#4A7896"]

    VEHICLE_COLORS = [
        "#315A86",  # Blue
        "#6A4C93",  # Purple
        "#8A4F5F",  # Burgundy
        "#4A7896",  # Cyan
    ]

    # ========================================================
    # THREE CHARTS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    # ========================================================
    # 1 - AVERAGE DELIVERY TIME BY CITY
    # ========================================================

    with col1:

        city_time = (
            filtered_df.groupby("City")["Time_taken(min)"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_city_time = px.bar(
            city_time,
            x="City",
            y="Time_taken(min)",
            title="Average Delivery Time by City",
            text="Time_taken(min)",
        )

        fig_city_time.update_traces(
            marker_color=CITY_COLORS,
            texttemplate="%{y:.2f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>City:</b> %{x}"
                "<br><b>Average Delivery Time:</b> %{y:.2f} min"
                "<extra></extra>"
            ),
        )

        fig_city_time.update_layout(
            height=320,
            margin=dict(t=55, b=30, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis=dict(
                title="Time (min)", range=[0, city_time["Time_taken(min)"].max() * 1.20]
            ),
        )

        st.plotly_chart(fig_city_time, width="stretch", key="delivery_city_time")

    # ========================================================
    # 2 - MOST ORDERED CITIES
    # ========================================================

    with col2:

        city_orders = filtered_df["City"].value_counts().reset_index()

        city_orders.columns = ["City", "Orders"]

        fig_city_orders = px.bar(
            city_orders,
            x="City",
            y="Orders",
            title="Most Ordered Cities",
            text="Orders",
        )

        fig_city_orders.update_traces(
            marker_color=CITY_ORDER_COLORS,
            texttemplate="%{y:,}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>City:</b> %{x}" "<br><b>Orders:</b> %{y:,}" "<extra></extra>"
            ),
        )

        fig_city_orders.update_layout(
            height=320,
            margin=dict(t=55, b=30, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis=dict(title="Orders", range=[0, city_orders["Orders"].max() * 1.20]),
        )

        st.plotly_chart(fig_city_orders, width="stretch", key="delivery_city_orders")

        # ========================================================
        # 3 - VEHICLE TYPE & TRAFFIC IMPACT ON DELIVERY TIME
        # ========================================================
    with col3:
        traffic_vehicle = (
            filtered_df.groupby(["Road_traffic_density", "Type_of_vehicle"])[
                "Time_taken(min)"
            ]
            .mean()
            .reset_index()
        )

        traffic_order = ["High", "Jam", "Low", "Medium"]

        traffic_vehicle["Road_traffic_density"] = pd.Categorical(
            traffic_vehicle["Road_traffic_density"],
            categories=traffic_order,
            ordered=True,
        )

        traffic_vehicle = traffic_vehicle.sort_values("Road_traffic_density")

        fig_vehicle_traffic = px.bar(
            traffic_vehicle,
            x="Road_traffic_density",
            y="Time_taken(min)",
            color="Type_of_vehicle",
            barmode="group",
            title="Average Delivery Time by Traffic Density and Vehicle Type",
            labels={
                "Road_traffic_density": "Traffic Density",
                "Time_taken(min)": "Average Delivery Time (min)",
                "Type_of_vehicle": "Vehicle Type",
            },
            color_discrete_sequence=[
                "#636EFA",  # electric_scooter
                "#EF553B",  # motorcycle
                "#00CC96",  # scooter
                "#AB63FA",  # bicycle
            ],
        )

        fig_vehicle_traffic.update_traces(
            texttemplate="%{y:.2f}",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=12),
            hovertemplate=(
                "<b>Traffic:</b> %{x}"
                "<br><b>Vehicle:</b> %{fullData.name}"
                "<br><b>Average Time:</b> %{y:.2f} min"
                "<extra></extra>"
            ),
        )

        fig_vehicle_traffic.update_layout(
            height=330,
            margin=dict(t=55, b=20, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )

        st.plotly_chart(
            fig_vehicle_traffic, width="stretch", key="vehicle_traffic_dashboard"
        )

# ============================================================
# TAB 4 - TRENDS & RELATIONSHIPS
# ============================================================

with tab4:

    st.header("📈 Trends & Relationships")

    col1, col2, col3 = st.columns(3)

    # ========================================================
    # 1. Multiple Deliveries & Delivery Time
    # ========================================================

    with col1:

        x = filtered_df["multiple_deliveries"]
        y = filtered_df["Time_taken(min)"]

        correlation = x.corr(y)

        slope, intercept = np.polyfit(x, y, 1)

        x_line = np.array([x.min(), x.max()])
        y_line = slope * x_line + intercept

        fig_multi_time = px.scatter(
            x=x,
            y=y,
            title="Multiple Deliveries & Delivery Time",
            labels={"x": "Multiple Deliveries", "y": "Delivery Time (min)"},
        )

        # Trend Line
        fig_multi_time.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Trend Line",
                line=dict(color="red", width=5),
            )
        )

        # Correlation value
        fig_multi_time.add_annotation(
            x=0.5,
            y=1.12,
            xref="paper",
            yref="paper",
            text=f"Correlation (r) = {correlation:.2f}",
            showarrow=False,
            font=dict(color="white", size=14),
        )

        fig_multi_time.update_traces(
            selector=dict(mode="markers"),
            marker=dict(size=6, opacity=0.45),
            hovertemplate=(
                "<b>Multiple Deliveries:</b> %{x}"
                "<br><b>Delivery Time:</b> %{y:.1f} min"
                "<extra></extra>"
            ),
        )

        fig_multi_time.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(
                title="Multiple Deliveries", tickmode="linear", dtick=1, showgrid=True
            ),
            yaxis=dict(title="Delivery Time (min)", showgrid=True),
            legend=dict(orientation="h", y=1.02, x=0),
        )

        st.plotly_chart(
            fig_multi_time, width="stretch", key="trends_multiple_delivery_time"
        )

    # Multiple Deliveries & Rating
    with col2:
        x = filtered_df["multiple_deliveries"]
        y = filtered_df["Delivery_person_Ratings"]

        correlation = x.corr(y)

        slope, intercept = np.polyfit(x, y, 1)

        x_line = np.array([x.min(), x.max()])
        y_line = slope * x_line + intercept

        fig_multi_rating = px.scatter(
            x=x,
            y=y,
            title="Multiple Deliveries & Rating",
            labels={"x": "Multiple Deliveries", "y": "Rating"},
        )

        # Trend Line
        fig_multi_rating.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Trend Line",
                line=dict(color="#EF553B", width=4),
            )
        )

        # Correlation
        fig_multi_rating.add_annotation(
            x=0.5,
            y=1.12,
            xref="paper",
            yref="paper",
            text=f"Correlation (r) = {correlation:.2f}",
            showarrow=False,
            font=dict(color="white", size=14),
        )

        # Points
        fig_multi_rating.update_traces(
            selector=dict(mode="markers"),
            marker=dict(size=5, color="#00D9FF", opacity=0.45),
            hovertemplate=(
                "<b>Multiple Deliveries:</b> %{x}"
                "<br><b>Rating:</b> %{y:.2f}"
                "<extra></extra>"
            ),
        )

        fig_multi_rating.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(
                title="Multiple Deliveries", tickmode="linear", dtick=1, showgrid=True
            ),
            yaxis=dict(title="Rating", showgrid=True),
            legend=dict(orientation="h", y=1.02, x=0),
        )

        st.plotly_chart(
            fig_multi_rating, width="stretch", key="trends_multiple_delivery_rating"
        )

    # ========================================================
    # 3. Distance & Traffic Impact on Delivery Time
    # ========================================================

    with col3:

        distance_data = filtered_df.copy()

        distance_data["Distance_Group"] = pd.cut(
            distance_data["Delivery_Distance_km"],
            bins=[0, 5, 10, 15, 20, 25],
            labels=["0-5 km", "5-10 km", "10-15 km", "15-20 km", "20-25 km"],
            include_lowest=True,
        )

        distance_traffic = (
            distance_data.groupby(
                ["Distance_Group", "Road_traffic_density"], observed=True
            )["Time_taken(min)"]
            .mean()
            .reset_index()
        )

        fig_distance_traffic = px.scatter(
            distance_traffic,
            x="Distance_Group",
            y="Time_taken(min)",
            color="Road_traffic_density",
            size="Time_taken(min)",
            title="Distance & Traffic Impact on Delivery Time",
            labels={
                "Distance_Group": "Delivery Distance",
                "Time_taken(min)": "Average Delivery Time (min)",
                "Road_traffic_density": "Traffic Density",
            },
        )

        fig_distance_traffic.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(title="Delivery Distance", showgrid=True),
            yaxis=dict(title="Average Delivery Time (min)", showgrid=True),
            legend=dict(title="Traffic Density"),
        )

        st.plotly_chart(
            fig_distance_traffic, width="stretch", key="trends_distance_traffic"
        )
# =========================================================
# TAB 5 — WEATHER & TRAFFIC
# =========================================================

with tab5:

    st.header("🌦️ Weather & Traffic")

    col1, col2 = st.columns(2)

    # ==========================================
# WEATHER CONDITIONS - NUMBER OF ORDERS
# ==========================================

with col1:

    weather_orders = filtered_df["Weatherconditions"].value_counts().reset_index()

    weather_orders.columns = ["Weather", "Orders"]

    fig_weather_orders = px.bar(
        weather_orders,
        x="Weather",
        y="Orders",
        title="Orders by Weather Condition",
        text="Orders",
        color="Weather",
        color_discrete_sequence=["#8FA8FF", "#A78BFA", "#6D7FD8", "#B08BC4", "#5B6FB5"],
    )

    fig_weather_orders.update_traces(
        texttemplate="%{y:,}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>Weather:</b> %{x}" "<br><b>Orders:</b> %{y:,}" "<extra></extra>"
        ),
    )

    fig_weather_orders.update_layout(
        height=300,
        margin=dict(t=50, b=20, l=10, r=10),
        yaxis=dict(range=[0, weather_orders["Orders"].max() * 1.15]),
    )

    st.plotly_chart(fig_weather_orders, width="stretch", key="weather_orders_chart")

# ==========================================
# AVERAGE DELIVERY TIME BY WEATHER
# ==========================================

with col2:

    weather_time = (
        filtered_df.groupby("Weatherconditions")["Time_taken(min)"]
        .mean()
        .sort_values()
        .reset_index()
    )

    fig_weather_time = go.Figure()

    # Lines
    for _, row in weather_time.iterrows():
        fig_weather_time.add_trace(
            go.Scatter(
                x=[0, row["Time_taken(min)"]],
                y=[row["Weatherconditions"], row["Weatherconditions"]],
                mode="lines",
                line=dict(color="#5B6FB5", width=4),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Dots + Values
    fig_weather_time.add_trace(
        go.Scatter(
            x=weather_time["Time_taken(min)"],
            y=weather_time["Weatherconditions"],
            mode="markers+text",
            marker=dict(size=14, color="#A78BFA"),
            text=weather_time["Time_taken(min)"],
            textposition="middle right",
            texttemplate="%{text:.2f}",
            textfont=dict(size=13),
            hovertemplate=(
                "<b>Weather:</b> %{y}"
                "<br><b>Average Delivery Time:</b> %{x:.2f} min"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig_weather_time.update_layout(
        title="Average Delivery Time by Weather",
        xaxis_title="Average Delivery Time (min)",
        yaxis_title="Weather",
        height=300,
        margin=dict(t=50, b=20, l=10, r=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )

    st.plotly_chart(fig_weather_time, width="stretch", key="weather_average_time")

# =========================
# Tab 6: Delivery Persons
# =========================

with tab6:

    st.markdown("## 🏆 Delivery Persons")

    # =========================
    # Delivery Person Analysis
    # =========================

    delivery_analysis = (
        filtered_df.groupby("Delivery_person_ID")
        .agg(
            Avg_Rating=("Delivery_person_Ratings", "mean"),
            Total_Orders=("Delivery_person_ID", "count"),
            Avg_Delivery_Time=("Time_taken(min)", "mean"),
            Age=("Delivery_person_Age", "mean"),
            Multiple_Delivery_Orders=("multiple_deliveries", lambda x: (x > 0).sum()),
        )
        .reset_index()
    )

    # =========================
    # Best 10
    # =========================

    best_delivery = (
        delivery_analysis.sort_values(
            ["Avg_Rating", "Total_Orders"], ascending=[False, False]
        )
        .head(10)
        .copy()
    )

    # =========================
    # Worst 10
    # =========================

    worst_delivery = (
        delivery_analysis.sort_values(
            ["Avg_Rating", "Total_Orders"], ascending=[True, True]
        )
        .head(10)
        .copy()
    )

    # Round values

    best_delivery["Avg_Rating"] = best_delivery["Avg_Rating"].round(2)

    best_delivery["Avg_Delivery_Time"] = best_delivery["Avg_Delivery_Time"].round(1)

    best_delivery["Age"] = best_delivery["Age"].round().astype(int)

    worst_delivery["Avg_Rating"] = worst_delivery["Avg_Rating"].round(2)

    worst_delivery["Avg_Delivery_Time"] = worst_delivery["Avg_Delivery_Time"].round(1)

    worst_delivery["Age"] = worst_delivery["Age"].round().astype(int)

    # =========================
    # Three Columns
    # =========================

    col1, col2, col3 = st.columns([1.2, 1, 1])

    # =========================
    # Top 10 Chart
    # =========================

    with col1:

        st.markdown("### ⭐ Top 10")

        chart_data = best_delivery.sort_values("Avg_Rating", ascending=True)

        fig = px.bar(
            chart_data,
            x="Avg_Rating",
            y="Delivery_person_ID",
            orientation="h",
            text="Avg_Rating",
        )

        fig.update_traces(
            marker_color="#8FA8FF",
            texttemplate="%{x:.2f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>Delivery Person:</b> %{y}"
                "<br><b>Rating:</b> %{x:.2f}"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            height=420,
            margin=dict(t=10, b=10, l=5, r=25),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(title="Rating", range=[0, 5.3], showgrid=False),
            yaxis=dict(title=None, tickfont=dict(size=8)),
            showlegend=False,
        )

        st.plotly_chart(fig, width="stretch", key="top_10_delivery_persons")

    # =========================
    # Best 10 Table
    # =========================

    with col2:

        st.markdown("### 🥇 Best 10")

        best_display = best_delivery[
            [
                "Delivery_person_ID",
                "Avg_Rating",
                "Total_Orders",
                "Avg_Delivery_Time",
                "Age",
                "Multiple_Delivery_Orders",
            ]
        ].copy()

        best_display.columns = [
            "Person ID",
            "Rating",
            "Orders",
            "Avg Time",
            "Age",
            "Multiple",
        ]

        st.dataframe(
            best_display, hide_index=True, use_container_width=True, height=420
        )

    # =========================
    # Worst 10 Table
    # =========================

    with col3:

        st.markdown("### ⚠️ Worst 10")

        worst_display = worst_delivery[
            [
                "Delivery_person_ID",
                "Avg_Rating",
                "Total_Orders",
                "Avg_Delivery_Time",
                "Age",
                "Multiple_Delivery_Orders",
            ]
        ].copy()

        worst_display.columns = [
            "Person ID",
            "Rating",
            "Orders",
            "Avg Time",
            "Age",
            "Multiple",
        ]

        st.dataframe(
            worst_display, hide_index=True, use_container_width=True, height=420
        )

# =========================
# Tab 7: Insights & Relationships
# =========================

with tab7:

    st.markdown("## 💡 Insights & Relationships")

    insights = [
        (
            "🚦 Traffic Density & Delivery Time",
            "Higher traffic density is associated with longer delivery times. "
            "Jam traffic has the highest average delivery time, while Low traffic "
            "has the lowest. The correlation is 0.42.",
        ),
        (
            "📦 Multiple Deliveries & Delivery Time",
            "More multiple deliveries are associated with longer delivery times. "
            "Average delivery time increases as the number of additional deliveries "
            "increases. The correlation is 0.38.",
        ),
        (
            "⭐ Delivery Time & Customer Rating",
            "Longer delivery times are associated with lower customer ratings. "
            "The correlation is -0.28.",
        ),
        (
            "🏙️ City & Delivery Time",
            "Semi-Urban areas have the highest average delivery time and a "
            "noticeably lower order volume compared with Urban and Metropolitan areas.",
        ),
        (
            "🍽️ Restaurant Locations & Delivery Persons",
            "After the data gap, the number of unique recorded restaurant locations "
            "increased, along with an increase in recorded delivery persons, "
            "and a noticeable increase in the total number of orders.",
        ),
        (
            "🕐 Daily Order Trend & Recorded Working Hours",
            "The alternating daily order pattern is associated with differences "
            "in recorded operating hours. Some days contain approximately 18 hours "
            "of recorded activity, while the following days contain only about "
            "10 hours, creating the recurring up-and-down pattern in daily orders.",
        ),
        (
            "⚠️ Missing Date Coverage",
            "No orders are recorded from February 19 to February 28, 2022, "
            "indicating a gap in the dataset's date coverage. ",
        ),
    ]

    # =========================
    # Display Insights
    # =========================

    for i in range(0, len(insights), 2):

        col1, col2 = st.columns(2)

        with col1:

            title, text = insights[i]

            with st.container(border=True):

                st.markdown(f"### {title}")
                st.write(text)

        if i + 1 < len(insights):

            with col2:

                title, text = insights[i + 1]

                with st.container(border=True):

                    st.markdown(f"### {title}")
                    st.write(text)

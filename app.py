import streamlit as st
import pydeck as pdk
import pandas as pd

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Sidebar 1
st.sidebar.title("SuperShopper")

st.sidebar.write("Where do you want to shop?")

# Main content
data = pd.read_csv("2018-2023_final_data_with_weather_normalised.csv", low_memory=False)
org_data = data.copy()

# time_of_day = {"12AM": 0,"1AM": 1,"2AM": 2,"3AM": 3,"4AM": 4,"5AM": 5,"6AM": 6,"7AM": 7,"8AM": 8,"9AM": 9,"10AM": 10,"11AM": 11,"12PM": 12,"1PM": 13,"2PM": 14,"3PM": 15,"4PM": 16,"5PM": 17,"6PM": 18,"7PM": 19,"8PM": 20,"9PM": 21,"10PM": 22,"11PM": 23}

days = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Black Friday": 5, "Sat": 6, "Sun": 7, "Cyber Monday": 8, "Tue ": 9, "Wed ": 10, "Thu ": 11, "Fri ": 12, "Sat ": 13, "Sun ": 14}


# Add selection for day
day = st.segmented_control("Select day", list(days.keys()), label_visibility="hidden")

slider_disabled = bool(day)
if slider_disabled:
    data = data[(data["week"] == days[day])]


# Filter by brand
discount_data = pd.read_csv("discounts.csv")
# filter the brands based on discount selected in slider
selected_discount = st.sidebar.slider("Select discount", min_value=0, max_value=100, value=0, step=5, format="%d%%")

brands = discount_data[discount_data["discounts"] >= int(selected_discount)]["brands"]

selected_brand = st.sidebar.pills("Select store", brands, label_visibility="hidden")
if selected_brand:
    data = data[data["brands"] == selected_brand]
else:
    data = data

# Filter by store ID
selected_store_id = None
if selected_brand:
    store_ids = data["street_address"].unique()
    selected_store_id = st.sidebar.selectbox("Which store?", store_ids, index=None, placeholder="Select store", label_visibility="hidden")
    if selected_store_id:
        data = data[data["street_address"] == selected_store_id]
    else:
        data = data

    lat = data["latitude"].mean()
    lon = data["longitude"].mean()
else:
    lat = 40.703
    lon = -74.000



# Define a layer to display on a map
layer = pdk.Layer(
    "ScatterplotLayer",
    data=data.groupby(["brands","store_id","street_address", "latitude","longitude"])['counts'].mean().reset_index(),
    get_position=["longitude","latitude"],
    get_radius='60',
    get_color="[255, 75, 75]",
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    auto_highlight=True,
)


# Set the viewport location
view_state = pdk.ViewState(
    longitude=lon, latitude=lat, zoom=12, min_zoom=5, max_zoom=15, pitch=29.5, bearing=-1.36
)

# Render the deck.gl map
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{brands}\n{street_address}"},)

# Display the map
st.pydeck_chart(r, use_container_width=True)

# read css file 
with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


col1, col2 = st.columns(2)

with col1:
    # Create a chart of the visits by hour
    st.write("Visits by hour")

    chart_data = org_data.copy()
    chart_data = chart_data[(chart_data["hour_of_day"] > 9)]
    if slider_disabled:
        chart_data = chart_data[(chart_data["week"] == days[day])]

    if selected_store_id:
        chart_data = chart_data[(chart_data["street_address"] == selected_store_id)]

    if selected_brand:
        chart_data = chart_data[(chart_data["brands"] == selected_brand)]
    chart_data = chart_data.groupby("hour_of_day")["counts"].sum().reset_index()

    st.line_chart(chart_data, y='counts', x='hour_of_day', x_label="Hour of Day", y_label="Visits", use_container_width=True)

with col2:
    # Create a chart for the visits & discounts by store
    st.write("Visits by Store")
    chart2_data = org_data.copy()
    if slider_disabled:
        chart2_data = chart2_data[(chart2_data["week"] == days[day])]
    if selected_brand:
        chart2_data = chart2_data[(chart2_data["brands"] == selected_brand)]
        chart2_data = chart2_data.groupby("street_address")["counts"].sum().reset_index()
        st.bar_chart(chart2_data, x='street_address', y='counts', x_label="Store", y_label="Visits", use_container_width=True)
    else:
        chart2_data = chart2_data.groupby("brands")["counts"].sum().reset_index()
        st.bar_chart(chart2_data, x='brands', y=['counts'], x_label="Brand", y_label="Visits", use_container_width=True)

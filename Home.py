import os
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from PIL import Image
from datetime import datetime

st.set_page_config(layout="wide")

# ---------- CACHING MONGODB CONNECTION ----------
@st.cache_resource
def get_mongo_client():
    return MongoClient("mongodb://localhost:27017/")

client=get_mongo_client()
db=client["mydatabase"]
collection=db["property_data"]
log_collection=db["update_logs"]  # New collection for logs

# ---------- STREAMLIT SETUP ----------
colA, colB = st.columns([1, 8])
with colA:
    if st.button("View Status Chart"):
        st.switch_page("pages/Convertible_Status_Chart.py")

with colB:
    st.markdown("<h1 style='text-align:center;'>PropMarker Validation Tool</h1>", unsafe_allow_html=True)

# ---------- FILTER FORM ----------
col1, col2 = st.columns([1, 1])
with col1:
    source = st.selectbox("Source",["Zoopla","Rightmove"])
with col2:
    convertible_status = st.selectbox("Convertible status", [1, 2, 3, 4])

col3, col4 = st.columns([1, 1])
with col3:
    date_from = st.date_input("Date Range From")
with col4:
    date_to = st.date_input("Date Range To")

# Search button
if st.button("Search"):
    date_from_dt = datetime.combine(date_from, datetime.min.time())
    date_to_dt = datetime.combine(date_to, datetime.max.time())
    date_from_str = date_from_dt.strftime("%Y-%m-%dT00:00:00.000Z")
    date_to_str = date_to_dt.strftime("%Y-%m-%dT00:00:00.000Z")
    source_str = source.lower()

    query = {
        "convertible_status": convertible_status,
        "etl_load_timestamp": {
            "$gte": date_from_str,
            "$lte": date_to_str
        },
        "prop_flp[0]": {"$regex": source_str, "$options": "i"},
        "update_timestamp": {"$exists": False}
    }

    results = list(collection.find(query))

    if not results:
        st.warning(f"No records found for source '{source}' in the selected date range.")
        st.session_state.results = []
        st.session_state.show_counts = True
    else:
        st.session_state.current_index = 0
        st.session_state.results = results
        st.session_state.show_counts = False

# ---------- DISPLAY RESULTS ----------
if "results" in st.session_state and st.session_state.results:
    current = st.session_state.current_index
    total = len(st.session_state.results)

    if 0 <= current < total:
        doc = st.session_state.results[current]

        col_img1, col_img2, col_img3 = st.columns([1,1,1])
        with col_img2:
            st.image(doc.get("prop_flp[0]", ""), caption=f"Image {current + 1} of {total}", width=400)

        col_spacer1, col_prev, col_spacer2, col_next, col_spacer3 = st.columns([2,1,4,1,2])
        with col_prev:
            if st.button("Previous"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.session_state.show_counts = False
                    st.rerun()

        with col_next:
            if st.button("Next"):
                if st.session_state.current_index < total - 1:
                    st.session_state.current_index += 1
                    st.session_state.show_counts = False
                    st.rerun()

        col8, col9, col10 = st.columns([1, 1, 1])
        with col8:
            st.write(f"PID : {doc['pid']}")
        with col9:
            st.write(f"Property Type : {doc['filter_property_type']}")
        with col10:
            st.write(f"Convertible Status : {doc['convertible_status']}")

        col11, col12, col13, col14 = st.columns([1, 1, 1, 1])
        with col11:
            pid = st.text_input("PID")
        with col12:
            property_type = st.selectbox("Property type", ["Flat", "House", "HMO"])
        with col13:
            convertible_status = st.selectbox("Convertible status", ["1-Not Convertible", "2-Convertible"])
        with col14:
            comment = st.text_input("Comment")

        spacer, submit_col = st.columns([9, 1])
        with submit_col:
            if st.button("Submit"):
                current_date_str = datetime.now().strftime("%Y-%m-%dT00:00:00.000Z")
                status_val = int(convertible_status.split("-")[0])
                pid_int = int(pid)

                # Update property_data collection
                collection.update_one(
                    {"pid": pid_int},
                    {"$set": {
                        "update_timestamp": current_date_str,
                        "convertible_status": status_val,
                        "filter_property_type": property_type
                    }}
                )

                # Log into update_logs collection
                log_data = {
                    "source": source,
                    "pid": pid_int,
                    "image_link": doc.get("prop_flp[0]", ""),
                    "comment": comment,
                    "convertible_status": status_val,
                    "property_type": property_type,
                    "update_timestamp": current_date_str
                }
                log_collection.insert_one(log_data)

                # Optional CSV write
                csv_filename = "updation_data.csv"
                file_exists = os.path.isfile(csv_filename)
                df = pd.DataFrame([log_data])
                df.to_csv(csv_filename, mode='a', header=not file_exists, index=False)

                st.success("Database updated and logged successfully.")
                st.write(log_data)
    else:
        st.warning("No records found for the given filters.")
        st.session_state.current_index = 0
        st.session_state.results = []
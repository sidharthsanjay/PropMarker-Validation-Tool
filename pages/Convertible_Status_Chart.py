import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
 
# Streamlit page configuration
st.set_page_config(layout="wide")
st.markdown("## Convertible Status Distribution")
 
# MongoDB connection
@st.cache_resource
def get_mongo_client():
    return MongoClient("mongodb://localhost:27017/")
 
client = get_mongo_client()
db = client["mydatabase"]
collection = db["property_data"]
 
@st.cache_data
def get_status_counts():
    docs = collection.find({}, {"convertible_status": 1})
    counts = {}
    for doc in docs:
        status = doc.get("convertible_status")
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))
 
# Fetch and prepare data
counts = get_status_counts()
labels = [str(k) for k in counts.keys()]
sizes = list(counts.values())
 
def absolute_count(pct, all_vals):
    total = sum(all_vals)
    count = int(round(pct / 100. * total))
    return f'{count}'
 
# Create and display pie chart
fig, ax = plt.subplots(figsize=(2, 2), dpi=80) # You can experiment with figsize (e.g., 1.5, 1.5) and dpi (e.g., 70, 60)
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=labels,
    autopct=lambda pct: absolute_count(pct, sizes),
    startangle=90,
    explode=[0.05]*len(sizes),
    textprops={'fontsize': 8},
    wedgeprops=dict(width=0.4)
)
 
ax.axis('equal')
ax.set_title("Convertible Status", fontsize=10)
fig.tight_layout()
st.pyplot(fig)
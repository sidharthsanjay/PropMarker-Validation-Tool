# PropMarker Validation Tool

This Streamlit-based tool enables users to validate property listings stored in a MongoDB database. It allows filtering by source, date range, and convertible status, and provides the ability to update and log changes. It also includes a visualization dashboard for convertible status distribution.

## Features

* 🔍 **Filter Properties** by source, convertible status, and date range.
* 🖼️ **View Images** of properties with associated metadata.
* 📝 **Update & Log** property status directly into MongoDB and a local CSV file.
* 📊 **View Convertible Status Distribution** via a pie chart.
* 🔁 **Navigate through results** using Next/Previous buttons.

## Folder Structure

```
project-root/
│
├── Home.py                         # Main app interface
├── pages/
│   └── Convertible_Status_Chart.py # Chart visualization page
├── updation_data.csv               # (Generated) Log of updates
└── README.md
```

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/AlenKJ01/propmarker-validation-tool.git
   cd propmarker-validation-tool
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure MongoDB is running locally on `mongodb://localhost:27017/` and has the `mydatabase` with `property_data` and `update_logs` collections.

4. Run the app:

   ```bash
   streamlit run Home.py
   ```

## Notes

* Images are fetched from the `prop_flp[0]` field in the database.
* Updates are logged to a local `updation_data.csv` and a MongoDB collection (`update_logs`).
* Navigation to the chart view uses Streamlit's `st.switch_page`.

---


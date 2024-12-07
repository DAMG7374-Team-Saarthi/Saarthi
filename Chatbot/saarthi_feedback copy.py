import streamlit as st
import datetime
from saarthi_analytics import init_duckdb_connection, create_table, get_all_records, get_filtered_records

# Initialize connection and create table
@st.cache_resource
def init_db():
    conn = init_duckdb_connection()
    create_table(conn)
    return conn

conn = init_db()

st.title("Saarthi-- Dashboard")

# Create a form
with st.form(key='rating_date_form'):
    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)

    with col1:
        rating = st.selectbox("Select Rating", options=[1, 2, 3, 4, 5], key='rating')

    with col2:
        filter_date = st.date_input("Select Date", value=datetime.date.today(), key='date')

    # Submit button
    submit_button = st.form_submit_button(label='Apply Filters')

# Display records
if submit_button:
    # Get filtered records
    df = get_filtered_records(conn, rating, filter_date)
    st.write(f"Showing records with rating {rating} on {filter_date}")
else:
    # Get all records
    df = get_all_records(conn)
    # st.write("Showing all records")

# Display the dataframe
if df.empty:
    st.write("No records found.")
else:
    st.dataframe(df)

# Display record count
st.write(f"Total records: {len(df)}")
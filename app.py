import streamlit as st
import subprocess

st.set_page_config(page_title="Write YT Data", page_icon=":pencil:", layout="wide")

def fetch_data(start_date, end_date):
    # Run yt_analytics_v2.py with the provided dates
    command = f"python yt_analytics_v2.py --start_date {start_date} --end_date {end_date}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Error: {e}")
        return False
    return True

# Main Streamlit app
st.title(":pencil: Write YT Analytics Data to G-Sheets")


# Date input fields
start_date = st.date_input("Start Date", value=None, min_value=None, max_value=None, key=None)
end_date = st.date_input("End Date", value=None, min_value=None, max_value=None, key=None)

# Button to trigger data fetching
if st.button("Write Data"):
    # Use st.spinner for loading animation
    with st.spinner("Writing Data.."):

        # Fetch data in a separate thread to allow for the spinner to be displayed
        success = fetch_data(start_date, end_date)

    if success:
        # Display success message after data is written
        st.success("Data written successfully!")

        # Run the command to launch the dashboard
        st.balloons()
        st.info("Launching the dashboard...")
        subprocess.run(["python", "-m", "streamlit", "run", "dashboard.py"])
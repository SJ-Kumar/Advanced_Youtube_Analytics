import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import time
from yt_analytics_v2 import SPREADSHEET_ID
from compare_top_videos import compare_top_videos, write_to_spreadsheet_and_create_database

# Function to authenticate and get the Google Sheets data
def get_google_sheets_data(sheet_name):
    gc = gspread.service_account(filename='SERVICE_ACCOUNT.json')
    sh = gc.open_by_key(SPREADSHEET_ID)

    # Get all sheets in the spreadsheet
    sheets = sh.worksheets()

    for sheet in sheets:
        if sheet.title == sheet_name:
            worksheet = sheet
            break
    else:
        st.error(f"Sheet with name '{sheet_name}' not found in the spreadsheet.")
        return pd.DataFrame()  # Return an empty DataFrame if the sheet is not found

    # Get all values from the sheet
    data = worksheet.get_all_values()[1:]

    # Create a DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    return df

st.set_page_config(page_title="Youtube Analytics", page_icon=":bar_chart:", layout="wide")

st.markdown('<h1 style="text-align:center;">&#128202; YouTube Analytics</h1>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Specify the sheet names you want to load
sheets_to_load = ['Basic Stats','Top Videos', 'User Geography', 'Device and OS', 'Viewer Demographics', 'Traffic Source']

# Create a dictionary to store the DataFrames
dfs = {}

# Load data from Google Sheets
for sheet_name in sheets_to_load:
    dfs[sheet_name] = get_google_sheets_data(sheet_name)

# Display the loaded DataFrames
for sheet_name, df in dfs.items():
    #st.subheader(sheet_name)
    #st.write(df)
    with st.spinner(f"Loading {sheet_name} data..."):
        time.sleep(2)  

        if sheet_name == 'Basic Stats':
            # Example: Display total views, likes, and subscribers
            total_views = df['views'].astype(float).sum()
            total_likes = df['likes'].astype(float).sum()
            total_subscribers = df['subscribersGained'].astype(float).sum()

            st.markdown(
                f'<div style="display:flex; flex-direction:row ;justify-content:center;">'
                f'<div style="background-color:#4CAF50; padding:15px; border-radius:10px; margin-bottom:20px; margin-right:20px; width: 25%">'
                f'<h3 style="text-align:center; color:#fff; font-size:1.5rem;">Views</h3>'
                f'<p style="text-align:center; font-size:2rem; color:#fff; margin:0">{total_views:,.0f}</p>'
                f'</div>'
                f'<div style="background-color:#2196F3; padding:15px; border-radius:10px;  margin-bottom:20px; margin-right:20px; width: 25%">'
                f'<h3 style="text-align:center; color:#fff; font-size:1.5rem;">Likes</h3>'
                f'<p style="text-align:center; font-size:2rem; color:#fff; margin:0">{total_likes:,.0f}</p>'
                f'</div>'
                f'<div style="background-color:#FF9800; padding:15px;  margin-bottom:20px; border-radius:10px; width: 25%">'
                f'<h3 style="text-align:center; color:#fff; font-size:1.5rem;">New Subscribers</h3>'
                f'<p style="text-align:center; font-size:2rem; color:#fff; margin:0">{total_subscribers:,.0f}</p>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif sheet_name == 'Top Videos':
            st.markdown('<h1 style="text-align:center; margin-bottom:20px;">Top Videos</h1>', unsafe_allow_html=True)

            for index, row in df.iterrows():
                video_name = row['video']
                video_id = row['video_id']
                total_views = row['views']
                total_likes = row['likes']
                avg_view_percentage = row['averageViewPercentage']

                # Display video thumbnail and name
                col1, col2 = st.columns([1, 2])
                with col1:
                    thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                    st.image(thumbnail_url, caption=video_name, use_column_width=True)

                with col2:
                    # Create a hyperlink to the YouTube video
                    video_link = f'<a href="https://www.youtube.com/watch?v={video_id}" target="_blank"><h2>{video_name}</h2></a>'
                    st.markdown(video_link, unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="display:flex; flex-direction:row">'
                        f'<div style="background-color:#4CAF50; padding:10px; border-radius:10px; margin-bottom:10px; margin-right:15px; width: 33%">'
                        f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Views</h4>'
                        f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{total_views}</p>'
                        f'</div>'
                        f'<div style="background-color:#2196F3; padding:10px; border-radius:10px;margin-bottom:10px; margin-right:15px; width: 33%">'
                        f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Likes</h4>'
                        f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{total_likes}</p>'
                        f'</div>'
                        f'<div style="background-color:#FF9800; padding:10px; border-radius:10px;margin-bottom:10px; width: 33%">'
                        f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Avg. % Watched</h4>'
                        f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{avg_view_percentage}%</p>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
                    
        elif sheet_name == 'User Geography':
            # Use Streamlit columns to display the charts side by side
            col1, col2 = st.columns([1, 1])

            # Plot pie chart for User Geography
            with col1:
                st.subheader('User Geography')
                fig_user_geo = px.pie(df, names='country', values='views', title='Views by Country')
                st.plotly_chart(fig_user_geo)

        elif sheet_name == 'Device and OS':
            # Plot pie chart for Device and OS
            with col2:
                st.subheader('Device and OS')
                fig_device_os = px.pie(df, names='deviceType', values='views', title='Views by Device Type')
                st.plotly_chart(fig_device_os)

        elif sheet_name == 'Viewer Demographics':

        # Use Streamlit columns to display the charts side by side
            col1, col_space, col2 = st.columns([1, 0.1, 1])

        # Plot a funnel chart for viewer demographics
            with col1:
                st.subheader('Viewer Demographics')
                fig_funnel = px.funnel(
                df,
                x='viewerAge',
                y='viewerPercentage',
                color='viewerGender',
                title='Age and Gender of Viewers',
                labels={'viewerAge': 'Age Group', 'viewerPercentage': 'Viewer Percentage', 'viewerGender':'Gender'},
                )
                st.plotly_chart(fig_funnel)

        elif sheet_name == 'Traffic Source':        
            # Plot scatter or line chart for traffic source data
            with col2:
                st.subheader('Traffic Source')
                fig_traffic_source = px.scatter(df, x='trafficSource', y='views',
                                                title='Traffic Source by Views',
                                                labels={'views': 'Views'},
                                                )
                st.plotly_chart(fig_traffic_source)

st.sidebar.markdown('<h1 style="text-align:center; margin-bottom:20px;">Top Videos Comparison</h1>', unsafe_allow_html=True)

db_name_2022 = st.sidebar.text_input("Enter the name of the first database:")
db_name_2023 = st.sidebar.text_input("Enter the name of the second database:")

spreadsheet_id = SPREADSHEET_ID

if st.sidebar.button('Fetch Results'):
    # Check if both database names are entered
    if not db_name_2022 or not db_name_2023:
        st.sidebar.error("Please enter both database names.")
    else:
        # Compare top videos and write to spreadsheet and new databases
        compared_data, db_name_2022, db_name_2023 = compare_top_videos(db_name_2022, db_name_2023)
        write_to_spreadsheet_and_create_database(compared_data, SPREADSHEET_ID, 'Comparison Results', db_name_2022, db_name_2023)
        st.sidebar.success("Comparison results fetched and written to the spreadsheet!")

        # Add anchor link to the "Comparison Results" section
        st.sidebar.markdown('<a href="#comparison-results">Go to Comparison Results</a>', unsafe_allow_html=True)
        st.sidebar.empty()  # Close the sidebar

    # Load comparison results data from Google Sheets
    comparison_results_df = get_google_sheets_data('Comparison Results')

    # Display the loaded DataFrames for Comparison Results
    st.markdown('<h1 style="text-align:center; margin-bottom:20px;" id="comparison-results">Comparison Results</h1>', unsafe_allow_html=True)

    for index, row in comparison_results_df.iterrows():
        #print(row)
        #print(comparison_results_df.columns)

        # Access the data using positional index
        video_id= row.iloc[0]  # Assuming the first column (index 0) is the Video ID
        video_name = row.iloc[1]  # Assuming the second column (index 1) is the Video Title
        views_difference = int(row.iloc[2])  # Assuming the third column (index 2) is Views Difference
        likes_difference = int(row.iloc[3])  # Assuming the fourth column (index 3) is Likes Difference
        comments_difference = int(row.iloc[4])  # Assuming the fifth column (index 4) is Comments Difference
        shares_difference = int(row.iloc[5])  # Assuming the sixth column (index 5) is Shares Difference

           # Display video thumbnail and name
        col1, col2 = st.columns([1, 2])
        with col1:
                thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                st.image(thumbnail_url, caption=video_name, use_column_width=True)

        with col2:
            # Create a hyperlink to the YouTube video
            video_link = f'<a href="https://www.youtube.com/watch?v={video_id}" target="_blank"><h2>{video_name}</h2></a>'
            st.markdown(video_link, unsafe_allow_html=True)
            st.markdown(
                f'<div style="display:flex; flex-direction:row">'
                f'<div style="background-color:#4CAF50; padding:10px; border-radius:10px; margin-bottom:10px; margin-right:15px; width: 33%">'
                f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Views Difference</h4>'
                f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{views_difference}</p>'
                f'</div>'
                f'<div style="background-color:#2196F3; padding:10px; border-radius:10px;margin-bottom:10px; margin-right:15px; width: 33%">'
                f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Likes Difference</h4>'
                f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{likes_difference}</p>'
                f'</div>'
                f'<div style="background-color:#FF9800; padding:10px; border-radius:10px;margin-bottom:10px; margin-right:15px; width: 33%">'
                f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Comments Difference</h4>'
                f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{comments_difference}</p>'
                f'</div>'
                f'<div style="background-color:#FFBF00; padding:10px; border-radius:10px;margin-bottom:10px; width: 33%">'
                f'<h4 style="text-align:center; color:#fff; font-size:1.2rem;">Shares Difference</h4>'
                f'<p style="text-align:center; font-size:1.5rem; color:#fff; margin:0">{shares_difference}</p>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

# YT-SpreadSheet-Analysis

- Open Online Google Sheets using Margam Farms Account and Create a new spreadsheet and name it first and then click on share button on top right corner and paste this id - margamfarm@margamfarms-389613.iam.gserviceaccount.com and click Done.
- Copy the SpreadSheet ID from the URL in chrome. For example,  If the URL is like this -https://docs.google.com/spreadsheets/d/1yCl__w0AcPNC3P_k7VgXpy2MRVzX7vviWBIQ69bhrK0/edit#gid=0
The SpreadSheet ID is 1yCl__w0AcPNC3P_k7VgXpy2MRVzX7vviWBIQ69bhrK0
- Paste this ID inside the python code for the variable SPREADSHEET_ID
- Go the terminal and run the following python command
python yt_analytics_v2.py --start_date 2022-01-01 --end_date 2023-11-10
You can modify the dates in this command as per your requirements.

# YouTube Analytics Final Description

1. Implemented user-friendly input features allowing users to specify start and end dates, triggering dynamic data fetching from YouTube Analytics API.
 
2. Developed a Python program utilizing YouTube Data and Analytics APIs to retrieve detailed analytics for the OpenText HowTo channel.
     (i) Introduced modular functions for fetching diverse data types, including basic stats, top videos, audience retention, time-based metrics, and user geography.
 
3. Implemented seamless data storage in Google Sheets using the Google Sheets API for real-time collaboration and in MongoDB for enhanced flexibility.
 
4. Integrated the Streamlit framework with Python to craft an engaging and interactive dashboard. Presented analytics data in an engaging format, incorporating dynamic and informative charts using Plotly Express based on the stored information in Google Sheets.

## Dashboard

![Dashboard](https://github.com/SJ-Kumar/Advanced_Youtube_Analytics/blob/a9854e3a2c7bca2cc0a3ba09437a137652346f30/ytadv1.png)

![Dashboard](https://github.com/SJ-Kumar/Advanced_Youtube_Analytics/blob/a9854e3a2c7bca2cc0a3ba09437a137652346f30/ytadv2.png)

![Dashboard](https://github.com/SJ-Kumar/Advanced_Youtube_Analytics/blob/a9854e3a2c7bca2cc0a3ba09437a137652346f30/ytadv3.png)

![Dashboard](https://github.com/SJ-Kumar/Advanced_Youtube_Analytics/blob/a9854e3a2c7bca2cc0a3ba09437a137652346f30/ytadv4.png)

![Dashboard](https://github.com/SJ-Kumar/Advanced_Youtube_Analytics/blob/a9854e3a2c7bca2cc0a3ba09437a137652346f30/ytadv5.png)

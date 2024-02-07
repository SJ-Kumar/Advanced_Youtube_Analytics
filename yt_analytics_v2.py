import argparse
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread
from pymongo import MongoClient
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly', 'https://www.googleapis.com/auth/spreadsheets']

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = 'CLIENT_SECRET.json'
SPREADSHEET_ID = '1TLN8sg-lky6ujeCGWudbiVrM010C8mDYdASHBz7mxGs'

MONGO_CONNECTION_STRING = "mongodb+srv://jayanthkumar597:ekO7numbM1hpO23K@cluster0.0wjrnqw.mongodb.net/"

def transform_data(data, column_headers):
    transformed_data = []
    for row in data:
        row_dict = dict(zip(column_headers, row))
        transformed_data.append(row_dict)
    return transformed_data

# Function to insert data into MongoDB
def insert_data_into_mongodb(db_name, collection_name, data, column_headers):
    transformed_data = transform_data(data, column_headers)
    client = MongoClient(MONGO_CONNECTION_STRING)
    db_name = db_name.replace('/', '_')
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(transformed_data)

def get_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def execute_api_request(client_library_function, **kwargs):
    response = client_library_function(**kwargs).execute()
    return response

def write_data_to_spreadsheet(data, sheet_name, column_headers):
    gc = gspread.service_account(filename='SERVICE_ACCOUNT.json')
    sh = gc.open_by_key(SPREADSHEET_ID)
    
    try:
        # Try to open the sheet. If it doesn't exist, create a new one.
        worksheet = sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols="100")

    # Clear the existing data in the worksheet.
    worksheet.clear()

    # Write the column headers to the first row
    if column_headers:
        worksheet.insert_rows([column_headers], 2)

    # Write the data starting from the second row
    if data:
        # Create a list of lists from the data
        data_list = [list(map(str, row)) for row in data]

        # Insert the data into the worksheet
        worksheet.insert_rows(data_list, 3)

    db_name = f"youtube_analytics_2023_for_MF"

    insert_data_into_mongodb(db_name, sheet_name, data, column_headers)

def get_video_titles(youtube, video_ids):
    video_info = youtube.videos().list(
        part='snippet',
        id=','.join(video_ids)
    ).execute()
    titles = {}
    for video in video_info.get('items', []):
        video_id = video['id']
        title = video['snippet']['title']
        titles[video_id] = title
    return titles


def fetch_and_write_basic_stats(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='estimatedMinutesWatched,views,likes,subscribersGained',
        dimensions='day',
        sort='day',
        maxResults=100
    )
    column_headers = ['day', 'estimatedMinutesWatched', 'views', 'likes', 'subscribersGained']
    write_data_to_spreadsheet(response.get('rows', []), 'Basic Stats', column_headers)


def fetch_and_write_top_videos(youtubeAnalytics, start_date, end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration,averageViewPercentage',
        dimensions='video',
        sort='-views',
        maxResults=10
    )
    video_ids = [row[0] for row in response.get('rows', [])]
    column_headers = ['video', 'video_id', 'views', 'likes', 'comments', 'shares', 'estimatedMinutesWatched', 'averageViewDuration', 'averageViewPercentage']

    # Fetch video titles using YouTube Data API
    youtube = build('youtube', 'v3', developerKey='AIzaSyD0gbH6qSaSGJNhU4TsQH-Xs8genUcuGEc')
    video_titles = get_video_titles(youtube, video_ids)

    data = []
    for row in response.get('rows', []):
        video_id = row[0]
        views = row[1]
        likes = row[2]
        comments = row[3]
        shares = row[4]
        estimated_minutes_watched = row[5]
        average_view_duration = row[6]
        average_view_percentage = row[7]

        title = video_titles.get(video_id, 'Title Not Found')

        data.append([title, video_id, views, likes, comments, shares, estimated_minutes_watched, average_view_duration, average_view_percentage])

    write_data_to_spreadsheet(data, 'Top Videos', column_headers)



def fetch_and_write_audience_retention(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='averageViewPercentage,averageViewDuration',
        dimensions='day',
        maxResults=100
    )
    column_headers = ['day', 'averageViewPercentage', 'averageViewDuration']
    write_data_to_spreadsheet(response.get('rows', []), 'Audience Retention',column_headers)

def fetch_and_write_time_based_data(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,averageViewDuration,estimatedMinutesWatched,averageViewPercentage,subscribersGained',
        dimensions='day', 
        sort='day',
        maxResults=1000
    )
    column_headers = ['day', 'views', 'averageViewDuration', 'estimatedMinutesWatched', 'averageViewPercentage', 'subscribersGained']
    write_data_to_spreadsheet(response.get('rows', []), 'Time-based Data',column_headers)


def fetch_and_write_user_geography(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained',
        dimensions='country',
        sort='-views',
        maxResults=10
    )
    column_headers = ['country', 'views','estimatedMinutesWatched','averageViewDuration','averageViewPercentage','subscribersGained']
    write_data_to_spreadsheet(response.get('rows', []), 'User Geography',column_headers)

def fetch_and_write_traffic_source(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views',
        dimensions='insightTrafficSourceType',
        sort='-views',
        maxResults=20
    )
    column_headers = ['trafficSource', 'views']
    write_data_to_spreadsheet(response.get('rows', []), 'Traffic Source',column_headers)

def fetch_and_write_device_and_os(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='views',
        dimensions='deviceType,operatingSystem',
        sort='-views',
        maxResults=10
    )
    column_headers = ['deviceType', 'operatingSystem', 'views']
    write_data_to_spreadsheet(response.get('rows', []), 'Device and OS',column_headers)

def fetch_and_write_viewer_demographics(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='viewerPercentage',
        dimensions='ageGroup,gender',
        sort='gender,ageGroup',
        maxResults=10
    )
    column_headers = ['viewerAge','viewerGender', 'viewerPercentage']
    write_data_to_spreadsheet(response.get('rows', []), 'Viewer Demographics',column_headers)

def playbacklocation(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='estimatedMinutesWatched,views',
        dimensions='insightPlaybackLocationType',
        sort='-views',
        maxResults=50
    )
    column_headers = ['insightPlaybackLocationType','estimatedMinutesWatched', 'views']
    write_data_to_spreadsheet(response.get('rows', []), 'Playback Location',column_headers)

def socialshares(youtubeAnalytics,start_date,end_date):
    response = execute_api_request(
        youtubeAnalytics.reports().query,
        ids='channel==MINE',
        startDate=start_date,
        endDate=end_date,
        metrics='shares',
        dimensions='sharingService',
        sort='-shares',
        maxResults=50
    )
    column_headers = ['sharingService','shares']
    write_data_to_spreadsheet(response.get('rows', []), 'Social',column_headers)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTube Analytics Data Fetcher')
    parser.add_argument('--start_date', type=str, help='Start date for analytics data (YYYY-MM-DD)')
    parser.add_argument('--end_date', type=str, help='End date for analytics data (YYYY-MM-DD)')

    args = parser.parse_args()

    if not args.start_date or not args.end_date:
        parser.error('Please provide both start_date and end_date parameters.')

    # Disable OAuthlib's HTTPs verification when running locally.
    # *DO NOT* leave this option enabled when running in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    youtubeAnalytics = get_service()
    
    fetch_and_write_basic_stats(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_top_videos(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_audience_retention(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_time_based_data(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_user_geography(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_traffic_source(youtubeAnalytics, args.start_date, args.end_date)
    fetch_and_write_device_and_os(youtubeAnalytics, args.start_date, args.end_date)
    #fetch_and_write_viewer_demographics(youtubeAnalytics, args.start_date, args.end_date)
    playbacklocation(youtubeAnalytics, args.start_date, args.end_date)
    socialshares(youtubeAnalytics, args.start_date, args.end_date)
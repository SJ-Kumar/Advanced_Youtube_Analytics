from pymongo import MongoClient
import gspread
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def get_top_videos_data(db_name, collection_name):
    client = MongoClient("mongodb+srv://jayanthkumar597:ekO7numbM1hpO23K@cluster0.0wjrnqw.mongodb.net/")
    db = client[db_name]
    collection = db[collection_name]
    
    cursor = collection.find({}, {'video_id': 1, 'video': 1, 'views': 1, 'likes': 1, 'comments': 1, 'shares': 1})
    
    data = {}
    for document in cursor:
        video_id = document['video_id']
        video = document.get('video', 'video Not Found')
        views = document.get('views', 0)
        likes = document.get('likes', 0)
        comments = document.get('comments', 0)
        shares = document.get('shares', 0)
        data[video_id] = {'video': video, 'views': views, 'likes': likes, 'comments': comments, 'shares': shares}
    
    return data

def compare_top_videos(db_name_2022, db_name_2023):
    data_2022 = get_top_videos_data(db_name_2022, 'Top Videos')
    data_2023 = get_top_videos_data(db_name_2023, 'Top Videos')

    compared_data = []

    for video_id, stats_2022 in data_2022.items():
        stats_2023 = data_2023.get(video_id, {'video': 'video Not Found', 'views': 0, 'likes': 0, 'comments': 0, 'shares': 0})

        views_difference = stats_2023['views'] - stats_2022['views']
        likes_difference = stats_2023['likes'] - stats_2022['likes']
        comments_difference = stats_2023['comments'] - stats_2022['comments']
        shares_difference = stats_2023['shares'] - stats_2022['shares']

        compared_data.append([video_id, stats_2022['video'], views_difference, likes_difference, comments_difference, shares_difference])

    return compared_data, db_name_2022, db_name_2023

def write_to_spreadsheet_and_create_database(compared_data, spreadsheet_id, sheet_name, db_name_2022, db_name_2023):
    gc = gspread.service_account(filename='SERVICE_ACCOUNT.json')
    sh = gc.open_by_key(spreadsheet_id)

    try:
        worksheet = sh.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols="100")

    header_row = ['Video ID', 'Video Title', 'Views Difference', 'Likes Difference', 'Comments Difference', 'Shares Difference']

    # Clear existing data and write headers
    worksheet.clear()
    worksheet.insert_rows([header_row], 1)

    # Write data starting from the second row
    if compared_data:
        worksheet.insert_rows(compared_data, 2)

    # Create a new MongoDB database for compared data with a name of your choice
    new_db_name = f"comparison_MF_2022_2023"
    client = MongoClient("mongodb+srv://jayanthkumar597:ekO7numbM1hpO23K@cluster0.0wjrnqw.mongodb.net/")
    db = client[new_db_name]

    # Insert the comparison data into a collection within the new database
    comparison_collection = db['ComparisonResults']
    comparison_collection.insert_many([{
        'video_id': row[0],
        'video_title': row[1],
        'views_difference': row[2],
        'likes_difference': row[3],
        'comments_difference': row[4],
        'shares_difference': row[5]
    } for row in compared_data])

    # Drop the old databases
    #client.drop_database(db_name_2022)
    #client.drop_database(db_name_2023)

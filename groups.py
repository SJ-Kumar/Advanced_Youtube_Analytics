from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly"]

CLIENT_SECRETS_FILE = "CLIENT_SECRET.json"

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8081)
    return credentials

def get_group_items(youtube_analytics, group_id):
    group_items_request = youtube_analytics.groupItems().list(groupId=group_id)
    group_items_response = group_items_request.execute()
    return group_items_response.get("items", [])


def main():
    credentials = authenticate()
    youtube_analytics = build("youtubeAnalytics", "v2", credentials=credentials)

    groups_request = youtube_analytics.groups().list()
    groups_response = groups_request.execute()
    #print(groups_response)

    for group in groups_response.get("items", []):
        group_id = group["id"]
        group_title = group["snippet"]["title"]
        group_items = get_group_items(youtube_analytics, group_id)
        group_items_count = len(group_items)
        #group_status = group.get("snippet", {}).get("privacyStatus", "Unknown")
        
        print(f"Group ID: {group_id}")
        print(f"Group Title: {group_title}")
        print(f"Group Items(Videos) Count: {group_items_count}")
        #print(f"Privacy Status: {group_status}")
        print("\n")

        # Listing video ids under this group
        print("Videos in this group:")
        for item in group_items:
            video_id = item["resource"]["id"]
            print(f"Video ID: {video_id}")
        print("\n")

if __name__ == "__main__":
    main()
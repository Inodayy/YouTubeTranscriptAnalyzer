import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Get the path to the JSON key file and youtube api key from the environment variables
json_key_file = os.getenv('YOUTUBE_SERVICE_ACCOUNT_CREDS')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_video_details(video_id):
    
    # Load credentials from the JSON key file
    credentials = service_account.Credentials.from_service_account_file(
        json_key_file,
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
    )
    
    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=credentials, developerKey=YOUTUBE_API_KEY)

    try:
        # Make a request to the YouTube API to get video details
        request = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        )
        response = request.execute()

        # Extract relevant information from the API response
        items = response.get('items', [])
        if not items:
            raise ValueError(f"No video details found for the given video_id: {video_id}")

        # Print and store video details
        snippet = items[0]['snippet']
        print(f"Title: {snippet['title']}")
        print(f"Channel: {snippet['channelTitle']}")
        print(f"Thumbnail: {snippet['thumbnails']['default']['url']}")

        video_details = {
            'title': snippet['title'],
            'channel': snippet['channelTitle'],
            'thumbnail': snippet['thumbnails']['default']['url']
        }

        return video_details

    except Exception as e:
        # Handle exceptions and raise an error message
        raise ValueError(f"Error fetching video details for video_id: {video_id}. Error message: {str(e)}")

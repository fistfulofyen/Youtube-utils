from googleapiclient.discovery import build
import json
import re
from src.util import *

with open('config/config.json', 'r') as file:
    config = json.load(file)

PLAY_LIST = "Pandas Tutorials"
USER_NAME = "schafer5"
DEV_KEY = config['youtube']['api_key']

with build('youtube', 'v3', developerKey=DEV_KEY) as service:
    # edit here
    # get_playlist_duration(service, USER_NAME, PLAY_LIST, display=True)
    # get_most_popular_video(service, USER_NAME, PLAY_LIST, display=True)

    request = service.playlistItems().list(
        part='status',
        playlistId='UUCezIgC97PvUuR4_gbFUs5g'
    )
    response = request.execute()
    print_json(response)

# util.py
import json
import re


def print_json(data):
    print(json.dumps(data, indent=2))
    print()

def iso_duration_to_minutes(iso_duration) -> float:
    # Match minutes and seconds using regex
    match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return 0.0  # or raise ValueError("Invalid duration format")
    
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = int(match.group(2)) if match.group(2) else 0

    total_minutes = minutes + seconds / 60.0
    return round(total_minutes, 2)

def minutes_to_hours(minutes: float) -> str:
    '''Convert minutes to a string representation in hours and minutes.'''
    if minutes >= 60:
        h = int(minutes // 60)
        m = int(round(minutes % 60))
        return f"{h}h {m}m" if m > 0 else f"{h}h"
    else:
        return f"{round(minutes)}m"
    
def get_channel_id(service, user_name: str) -> str:
    '''
    Retrieve the channel ID for a given YouTube username.
    returns the channel ID as a string.
    '''
    request = service.channels().list(
        part='contentDetails,statistics',
        forUsername=user_name,
        maxResults=25
    )
    response = request.execute()
    return response['items'][0]['id']

def get_playlist_id(service, channel_id: str, playlist_name: str, display=False) -> str:
    '''
    Retrieve the playlist ID for a given playlist name and channel ID.
    returns the playlist ID as a string.
    '''
    request = service.playlists().list(
        part='contentDetails,snippet',
        channelId=channel_id,
        maxResults=3
    )
    response = request.execute()
    
    for item in response['items']:
        if item['snippet']['title'] == playlist_name:
            if display:
                print(f"Playlist: {item['snippet']['title']} (ID: {item['id']})")
            return item['id']
    
    raise ValueError(f"Playlist '{playlist_name}' not found.")

def get_video_ids(service, playlist_id: str, max_results: int = 50, display=False) -> list:
    '''
    Retrieve all video IDs from a given playlist ID.
    returns a list of video IDs.
    '''
    nextPageToken = None
    video_ids = []
    
    while True:
        pl_request = service.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=nextPageToken
        )
        pl_response = pl_request.execute()
        
        for item in pl_response['items']:
            video_id = item['contentDetails']['videoId']
            video_ids.append(video_id)

        nextPageToken = pl_response.get('nextPageToken')
        if not nextPageToken:
            break

    if display:
        print(f"Video IDs for playlist '{playlist_id}': {video_ids}")
    return video_ids

def get_video_durations(service, video_ids: list) -> float:
    '''
    Retrieve the total duration of videos given their IDs.
    returns the total duration in minutes (float).
    '''
    video_ids_str = ','.join(video_ids)

    vid_request = service.videos().list(
        part='contentDetails',
        id=video_ids_str
    )
    vid_response = vid_request.execute()
    
    total_duration = 0.0
    for item in vid_response['items']:
        duration = item['contentDetails']['duration']
        duration_minutes = iso_duration_to_minutes(duration)
        total_duration += duration_minutes
    
    return total_duration

# application
def get_playlist_duration(service, user_name: str, playlist_name: str, max_results: int = 50, display=False) -> str:
    '''
    Get the total duration of a playlist for a given user.
    Returns the total duration as a string in hours and minutes.
    '''
    channel_id = get_channel_id(service, user_name)
    playlist_id = get_playlist_id(service, channel_id, playlist_name)
    video_ids = get_video_ids(service, playlist_id, max_results)
    total_duration = get_video_durations(service, video_ids)
    
    if display:
        print(f"Total duration of '{playlist_name}': {minutes_to_hours(total_duration)}")
    return minutes_to_hours(total_duration)

def get_most_popular_video(service, user_name: str, playlist_name: str, max_results: int = 50, display=False) -> str:
    '''
    Get the most popular video from a playlist for a given user.
    Returns the video ID of the most popular video.
    '''
    channel_id = get_channel_id(service, user_name)
    playlist_id = get_playlist_id(service, channel_id, playlist_name)
    video_ids = get_video_ids(service, playlist_id, max_results)

    vid_request = service.videos().list(
        part='statistics',
        id=','.join(video_ids)
    )
    vid_response = vid_request.execute()

    most_popular_video = max(vid_response['items'], key=lambda x: int(x['statistics']['viewCount']))
    
    if display:
        print(f"link to most popular video ID: https://www.youtube.com/watch?v={most_popular_video['id']}")
    
    return most_popular_video['id']

def get_video_title(service, video_id: list, display=False) -> str:
    '''
    Get the title of a video given its ID.
    Returns the title as a string.
    '''
    
    ids_str = ','.join(video_id) if isinstance(video_id, list) else video_id
    if not ids_str:
        raise ValueError("Video ID cannot be empty.")
    
    titles = []

    for i in range(0, len(video_id), 50):
        batch_ids = video_id[i:i + 50]
        ids_str = ','.join(batch_ids)

        request = service.videos().list(
            part='snippet',
            id=ids_str
        )
        response = request.execute()

        for item in response.get('items', []):
            titles.append(item['snippet']['title'])

        if display:
            for vid_id, title in zip(batch_ids, titles[-len(batch_ids):]):
                print(f"  Title: {title}, video link: https://www.youtube.com/watch?v={vid_id}")

    return titles
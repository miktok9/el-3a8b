import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_authenticated_service():
    client_id = os.getenv('YT_CLIENT_ID')
    client_secret = os.getenv('YT_CLIENT_SECRET')
    refresh_token = os.getenv('YT_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("[delete] Missing YouTube credentials in environment!")
        return None
        
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )
    creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def main():
    print("=" * 60)
    print("YOUTUBE BAD VIDEO CLEANUP")
    print("=" * 60)
    yt = get_authenticated_service()
    if not yt:
        print("[delete] Cannot authenticate to YouTube API.")
        return
        
    known_bad_ids = ["nq6-lKRMSxc"]
    
    # 1. Directly delete known bad video IDs
    for vid in known_bad_ids:
        try:
            print(f"[delete] Attempting to delete specific video ID: {vid}...")
            yt.videos().delete(id=vid).execute()
            print(f"[delete] ✅ SUCCESS: Deleted video {vid}")
        except Exception as e:
            print(f"[delete] Notice for {vid}: {e}")
            
    # 2. Scan recent uploads for any video containing error keywords in title/description
    try:
        channels_res = yt.channels().list(mine=True, part='contentDetails').execute()
        items = channels_res.get('items', [])
        if not items:
            print("[delete] No channel found.")
            return
            
        uploads_playlist = items[0]['contentDetails']['relatedPlaylists']['uploads']
        playlist_items = yt.playlistItems().list(playlistId=uploads_playlist, part='snippet', maxResults=30).execute()
        
        error_terms = ["credit", "top up", "top-up", "pollinations", "api key", "doesn't have enough"]
        
        for p_item in playlist_items.get('items', []):
            vid = p_item['snippet']['resourceId']['videoId']
            title = p_item['snippet']['title']
            desc = p_item['snippet']['description']
            combined = (title + " " + desc).lower()
            
            if any(term in combined for term in error_terms):
                print(f"[delete] Found bad video: '{title}' (ID: {vid})")
                try:
                    yt.videos().delete(id=vid).execute()
                    print(f"[delete] ✅ SUCCESS: Deleted bad video {vid} ('{title}')")
                except Exception as ex:
                    print(f"[delete] ❌ Failed to delete {vid}: {ex}")
                    
    except Exception as e:
        print(f"[delete] Error scanning channel uploads: {e}")

if __name__ == '__main__':
    main()

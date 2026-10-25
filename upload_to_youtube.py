"""
YouTube Upload Script - Optimized for YouTube Shorts
"""

import os
import re
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_authenticated_service():
    """Authenticate using refresh token from environment."""
    client_id = os.getenv('YT_CLIENT_ID')
    client_secret = os.getenv('YT_CLIENT_SECRET')
    refresh_token = os.getenv('YT_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing credentials! Set these environment variables / GitHub Secrets:\n"
            "  - YT_CLIENT_ID\n"
            "  - YT_CLIENT_SECRET\n"
            "  - YT_REFRESH_TOKEN"
        )
    
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


def sanitize_youtube_title(title: str) -> str:
    if not title:
        return "Ancient History #Shorts"
    title = title.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    title = " ".join(title.split()).strip("|-–— ")
    if len(title) > 100:
        title = title[:97] + "..."
    if not title or len(title.strip()) < 2:
        title = "Ancient History #Shorts"
    return title


def upload_to_youtube(video_file, title, description, tags=None, category_id='22'):
    """Upload video to YouTube and return result."""
    clean_title = sanitize_youtube_title(title)
    if not tags:
        tags = [
            "Ancient History", "Greek Mythology", "Ιστορία", "Αρχαία Ελλάδα",
            "Μυθολογία", "Shorts", "History", "Ancient Greece", "Womens History"
        ]
        
    youtube = get_authenticated_service()
    
    body = {
        'snippet': {
            'title': clean_title,
            'description': description or "",
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }
    
    if '#Shorts' not in body['snippet']['description']:
        body['snippet']['description'] += '\n\n#Shorts'
    
    media = MediaFileUpload(
        str(video_file),
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )
    
    print(f"[youtube] Uploading: {clean_title}")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Progress: {int(status.progress() * 100)}%")
    
    video_id = response['id']
    video_url = f"https://youtube.com/shorts/{video_id}"
    print(f"[youtube] ✅ Uploaded! Video ID: {video_id}")
    print(f"[youtube] URL: {video_url}")
    return {
        'status': 'success',
        'id': video_id,
        'platform': 'youtube',
        'link': video_url
    }


def main():
    """Upload the generated video to YouTube."""
    video_file = Path('output/final_video.mp4')
    if not video_file.exists():
        print("[youtube] ❌ No video found at output/final_video.mp4")
        return

    topic_file = Path('output/topic.txt')
    topic = "Ancient History"
    if topic_file.exists():
        topic = topic_file.read_text(encoding='utf-8').replace(' and ', ' και ').strip() or topic

    story_greek = ""
    story_greek_file = Path('output/story.txt')
    if story_greek_file.exists():
        story_greek = story_greek_file.read_text(encoding='utf-8').strip()

    story_en = ""
    story_en_file = Path('output/story_en.txt')
    if story_en_file.exists():
        story_en = story_en_file.read_text(encoding='utf-8').strip()

    # Create clean title
    if len(topic) + len(" | Ancient History #Shorts") <= 100:
        title = f"{topic} | Ancient History #Shorts"
    elif len(topic) + len(" #Shorts") <= 100:
        title = f"{topic} #Shorts"
    else:
        title = f"{topic[:85]}... #Shorts"

    # Create clean bilingual description
    desc_lines = [f"🏛️ {topic}", ""]
    if story_greek:
        desc_lines.append(story_greek)
        desc_lines.append("")
    if story_en:
        desc_lines.append("📖 English Translation:")
        desc_lines.append(story_en)
        desc_lines.append("")
    desc_lines.extend([
        "✨ Subscribe for daily stories from ancient history and mythology!",
        "🔔 Turn on notifications so you never miss a daily Short.",
        "",
        "#Shorts #AncientHistory #History #GreekMythology #AncientGreece #Mythology #WomensHistory"
    ])
    description = "\n".join(desc_lines)

    tags = [
        "Ancient History", "Greek Mythology", "Ιστορία", "Αρχαία Ελλάδα",
        "Μυθολογία", "Shorts", "History", "Ancient Greece", "Womens History"
    ]

    try:
        upload_to_youtube(
            video_file=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='22'
        )
    except Exception as e:
        print(f"[youtube] ❌ Upload failed: {e}")
        raise


if __name__ == '__main__':
    main()

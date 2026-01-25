"""
Multi-Platform Upload Script

Uploads videos to:
- YouTube Shorts
- Instagram Reels
- TikTok
- Facebook Reels

Each platform requires its own API credentials.
"""

import os
from pathlib import Path
import datetime

# Import platform-specific uploaders
from upload_to_youtube import upload_to_youtube
from upload_instagram import upload_to_instagram
from upload_tiktok import upload_to_tiktok
from upload_facebook import upload_to_facebook
from upload_threads import upload_to_threads
from upload_twitter import upload_to_twitter
from upload_vk import upload_to_vk

def main():
    """Upload video to all configured platforms."""
    video_file = Path('output/final_video.mp4')
    
    if not video_file.exists():
        print("[upload] ❌ No video found at output/final_video.mp4")
        return
    
    # Read story for metadata
    story_file = Path('output/story.txt')
    if story_file.exists():
        story = story_file.read_text(encoding='utf-8')
        # Use first sentence as title
        title_parts = story.split('.')
        title = title_parts[0][:100] if title_parts else "História das mulheres antigas"
    else:
        title = f"Ιστορία των Γυναικών στην Αρχαιότητα - {datetime.date.today()}"
    
    # Platform-specific content
    descriptions = {
        'youtube': f"{story[:150] if len(story) > 150 else story} #ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση",
        'instagram': f"{story[:2200] if len(story) > 2200 else story}\n\n#ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση #Shorts #Reels",
        'tiktok': f"{story[:2200] if len(story) > 2200 else story} #ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση #FYP",
        'facebook': f"{story[:63206] if len(story) > 63206 else story}\n\n#ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση",
        'threads': f"{story[:500] if len(story) > 500 else story} #ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση",
        'twitter': f"{story[:280] if len(story) > 280 else story} #ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία",
        'vk': f"{story[:220] if len(story) > 220 else story}\n\n#ΙστορίαΓυναικών #ΑρχαίαΙστορία #Ιστορία #Εκπαίδευση"
    }
    
    tags = [
        'Ιστορία', 'Αρχαίες Γυναίκες', 'Ιστορικά Γεγονότα',
        'Shorts', 'Reels', 'Εκπαίδευση', 'Πολιτισμός'
    ]
    
    results = {}
    
    # Upload to YouTube
    if all([
        os.getenv('YT_CLIENT_ID'),
        os.getenv('YT_CLIENT_SECRET'),
        os.getenv('YT_REFRESH_TOKEN')
    ]):
        print("\n" + "="*60)
        print("📺 Uploading to YouTube...")
        print("="*60)
        try:
            result = upload_to_youtube(video_file, title, descriptions['youtube'], tags)
            results['youtube'] = result
            print(f"✅ YouTube: https://youtube.com/shorts/{result['id']}")
        except Exception as e:
            print(f"❌ YouTube failed: {e}")
            results['youtube'] = None
    else:
        print("⏭️  Skipping YouTube (credentials not set)")
    
    # Upload to Instagram
    if all([
        os.getenv('IG_ACCESS_TOKEN'),
        os.getenv('IG_USER_ID')
    ]):
        print("\n" + "="*60)
        print("📸 Uploading to Instagram...")
        print("="*60)
        try:
            result = upload_to_instagram(str(video_file), descriptions['instagram'])
            results['instagram'] = result
            print(f"✅ Instagram: Uploaded successfully")
        except Exception as e:
            print(f"❌ Instagram failed: {e}")
            results['instagram'] = None
    else:
        print("⏭️  Skipping Instagram (credentials not set)")
    
    # Upload to TikTok
    if os.getenv('TIKTOK_ACCESS_TOKEN'):
        print("\n" + "="*60)
        print("🎵 Uploading to TikTok...")
        print("="*60)
        try:
            result = upload_to_tiktok(video_file, title, descriptions['tiktok'])
            results['tiktok'] = result
            print(f"✅ TikTok: Uploaded successfully")
        except Exception as e:
            print(f"❌ TikTok failed: {e}")
            results['tiktok'] = None
    else:
        print("⏭️  Skipping TikTok (credentials not set)")
    
    # Upload to Facebook
    if all([
        os.getenv('FB_ACCESS_TOKEN'),
        os.getenv('FB_PAGE_ID')
    ]):
        print("\n" + "="*60)
        print("📘 Uploading to Facebook...")
        print("="*60)
        try:
            result = upload_to_facebook(video_file, descriptions['facebook'])
            results['facebook'] = result
            print(f"✅ Facebook: Uploaded successfully")
        except Exception as e:
            print(f"❌ Facebook failed: {e}")
            results['facebook'] = None
    else:
        print("⏭️  Skipping Facebook (credentials not set)")
    
    # Upload to Threads
    if all([
        os.getenv('THREADS_ACCESS_TOKEN'),
        os.getenv('THREADS_USER_ID')
    ]):
        print("\n" + "="*60)
        print("🧵 Uploading to Threads...")
        print("="*60)
        try:
            result = upload_to_threads(str(video_file), descriptions['threads'])
            results['threads'] = result
            print(f"✅ Threads: Uploaded successfully")
        except Exception as e:
            print(f"❌ Threads failed: {e}")
            results['threads'] = None
    else:
        print("⏭️  Skipping Threads (credentials not set)")
    
    # Upload to Twitter/X
    if all([
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET'),
        os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_SECRET')
    ]):
        print("\n" + "="*60)
        print("🐦 Uploading to Twitter/X...")
        print("="*60)
        try:
            result = upload_to_twitter(video_file, descriptions['twitter'])
            results['twitter'] = result
            print(f"✅ Twitter: Uploaded successfully")
        except Exception as e:
            print(f"❌ Twitter failed: {e}")
            results['twitter'] = None
    else:
        print("⏭️  Skipping Twitter (credentials not set)")
    
    # Upload to VK
    if all([
        os.getenv('VK_ACCESS_TOKEN'),
        os.getenv('VK_GROUP_ID')
    ]):
        print("\n" + "="*60)
        print("🇷🇺 Uploading to VK...")
        print("="*60)
        try:
            result = upload_to_vk(str(video_file), descriptions['vk'], title)
            results['vk'] = result
            print(f"✅ VK: Uploaded successfully")
        except Exception as e:
            print(f"❌ VK failed: {e}")
            results['vk'] = None
    else:
        print("⏭️  Skipping VK (credentials not set)")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Upload Summary")
    print("="*60)
    success_count = 0
    total_count = len(results)
    for platform, result in results.items():
        if result:
            status = "✅ Success"
            success_count += 1
        else:
            status = "❌ Failed"
        print(f"{platform.capitalize()}: {status}")
    print("="*60)
    print(f"Success Rate: {success_count}/{total_count} platforms")
    print("="*60)

if __name__ == '__main__':
    main()

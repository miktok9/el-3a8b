"""
Uploads generated reels to all connected social media platforms
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

upload_dir = Path(__file__).parent / "upload"
if upload_dir.exists() and str(upload_dir) not in sys.path:
    sys.path.insert(0, str(upload_dir))

upload_to_facebook = None
upload_to_instagram = None
upload_to_youtube = None
upload_to_vk = None
upload_to_telegram = None
upload_to_twitter = None
upload_to_threads = None
upload_to_tiktok = None

try:
    from upload_facebook import upload_to_facebook as fb_upload
    upload_to_facebook = fb_upload
except ImportError as e:
    print(f"[!] Facebook upload module not available: {e}")

try:
    from upload_instagram import upload_to_instagram as ig_upload
    upload_to_instagram = ig_upload
except ImportError as e:
    print(f"[!] Instagram upload module not available: {e}")

try:
    from upload_to_youtube import upload_to_youtube as yt_upload
    upload_to_youtube = yt_upload
except ImportError as e:
    print(f"[!] YouTube upload module not available: {e}")

try:
    from upload_vk import upload_to_vk as vk_upload
    upload_to_vk = vk_upload
except ImportError as e:
    print(f"[!] VK upload module not available: {e}")

try:
    from upload_telegram import upload_to_telegram as tg_upload
    upload_to_telegram = tg_upload
except ImportError as e:
    print(f"[!] Telegram upload module not available: {e}")

try:
    from upload_twitter import upload_to_twitter as tw_upload
    upload_to_twitter = tw_upload
except ImportError as e:
    print(f"[!] Twitter upload module not available: {e}")

try:
    from upload_threads import upload_to_threads as th_upload
    upload_to_threads = th_upload
except ImportError as e:
    print(f"[!] Threads upload module not available: {e}")

try:
    from upload_tiktok import upload_to_tiktok as tk_upload
    upload_to_tiktok = tk_upload
except ImportError as e:
    print(f"[!] TikTok upload module not available: {e}")


def sanitize_youtube_title(title):
    if not title:
        return 'Shorts'
    title = title.replace(chr(10), ' ').replace(chr(13), ' ').replace(chr(9), ' ')
    title = ' '.join(title.split())
    title = title.strip('"|-–— ')
    if len(title) > 100:
        title = title[:97] + '...'
    if not title or len(title.strip()) < 2:
        return 'Shorts'
    return title

def sanitize_story_text(text: str) -> str:
    if not text:
        return ""
    lower = text.lower()
    for kw in ["credit", "top up", "top-up", "pollinations", "api key", "quota", "balance"]:
        if kw in lower:
            return ""
    return text.strip()

def get_video_title():
    """Generate title for YouTube from topic or clean story."""
    try:
        topic_file = Path("output/topic.txt")
        if topic_file.exists():
            topic = topic_file.read_text(encoding="utf-8").replace(" and ", " και ").strip()
            if topic:
                return f"{topic[:60]} #Shorts"
                
        en_story = sanitize_story_text(get_english_story())
        if en_story:
            en_first = en_story.split(".")[0] if "." in en_story else en_story[:60]
            return f"{en_first[:60]} #Shorts"
            
        native_story = sanitize_story_text(get_native_story())
        if native_story:
            native_first = native_story.split(".")[0] if "." in native_story else native_story[:60]
            return f"{native_first[:60]} #Shorts"
            
        return "Ancient History #Shorts"
    except Exception:
        return "Ancient History #Shorts"


def get_latest_reel():
    fv = Path("output/final_video.mp4")
    if fv.exists():
        latest = fv
    else:
        video_dir = Path("output/video")
        if not video_dir.exists():
            print("No output/video directory found")
            return None
        reels = list(video_dir.glob("*/final_reel.mp4"))
        if not reels:
            print("No reels found in output/video directory")
            return None
        latest = max(reels, key=lambda p: p.stat().st_mtime)
    metadata_file = latest.parent / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
    topic = "Ancient History"
    topic_file = Path("output/topic.txt")
    if topic_file.exists():
        try:
            topic = topic_file.read_text(encoding="utf-8").replace(" and ", " και ").strip() or topic
        except Exception:
            pass
    elif metadata.get("category_english"):
        topic = metadata.get("category_english")

    return {
        "video_path": str(latest),
        "metadata": metadata,
        "category": topic,
        "phrases": metadata.get("phrases", [])
    }


def get_english_story():
    try:
        ef = Path("output/story_en.txt")
        if ef.exists():
            return sanitize_story_text(ef.read_text(encoding="utf-8"))
    except: pass
    return ""

def get_native_story():
    try:
        nf = Path("output/story.txt")
        if nf.exists():
            return sanitize_story_text(nf.read_text(encoding="utf-8"))
    except: pass
    return ""

def generate_caption(phrases, category, platform="facebook"):
    """Bilingual caption for Facebook/Instagram: Topic + Greek + English translation."""
    topic_file = Path("output/topic.txt")
    topic = category or "Ancient History"
    if topic_file.exists():
        try:
            t = topic_file.read_text(encoding="utf-8").replace(" and ", " και ").strip()
            if t: topic = t
        except Exception:
            pass
            
    en_text = get_english_story()
    native_text = get_native_story()

    caption_lines = [f"Ancient History: {topic}", ""]
    if native_text:
        caption_lines.append(native_text.strip())
        caption_lines.append("")
    if en_text:
        caption_lines.append("--- English Translation ---")
        caption_lines.append("")
        caption_lines.append(en_text.strip())
        caption_lines.append("")
    caption_lines.extend(["Like & follow for daily history!", ""])
    caption_lines.append("#ancienthistory #history #greekhistory #womenshistory #ancientgreece #mythology #shorts")
    return "\n".join(caption_lines)


def upload_to_all_platforms(video_path, caption, category, phrases=None, video_title=""):
    results = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "video": video_path,
        "uploads": {},
        "platforms_attempted": [],
        "platforms_successful": [],
        "platforms_skipped": [],
        "platforms_failed": []
    }

    print("\n" + "=" * 80)
    print("MULTI-PLATFORM UPLOAD")
    print("=" * 80)
    print(f"Video: {video_path}")
    print(f"Category: {category}")
    print(f"Caption length: {len(caption)} characters")
    print("=" * 80)

    if not Path(video_path).exists():
        print(f"[ERROR] Video file not found: {video_path}")
        return results

    platforms = [
        ("facebook", upload_to_facebook, "Facebook"),
        ("instagram", upload_to_instagram, "Instagram"),
        ("youtube", upload_to_youtube, "YouTube"),
        ("vk", upload_to_vk, "VK"),
        ("telegram", upload_to_telegram, "Telegram"),
        ("twitter", upload_to_twitter, "Twitter"),
        ("threads", upload_to_threads, "Threads"),
        ("tiktok", upload_to_tiktok, "TikTok"),
    ]

    for platform_name, upload_func, display_name in platforms:
        print(f"\n{display_name} UPLOAD...")
        results["platforms_attempted"].append(platform_name)

        if upload_func:
            try:
                upload_result = None
                if platform_name == "facebook":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "instagram":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "youtube":
                    yt_title = sanitize_youtube_title(video_title or category)
                    upload_result = upload_func(video_path, yt_title, caption, ["history", "ancient history", "greek mythology", "shorts", "womenshistory"])
                elif platform_name == "vk":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "telegram":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "twitter":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "threads":
                    upload_result = upload_func(video_path, caption)
                elif platform_name == "tiktok":
                    upload_result = upload_func(video_path, video_title or category, caption)
                if upload_result:
                    results["uploads"][platform_name] = upload_result
                    results["platforms_successful"].append(platform_name)
                else:
                    results["uploads"][platform_name] = {"status": "failed", "error": "Upload function returned None"}
                    results["platforms_failed"].append(platform_name)
            except Exception as e:
                error_msg = str(e)
                results["uploads"][platform_name] = {"status": "failed", "error": error_msg}
                results["platforms_failed"].append(platform_name)
                print(f"  Error: {error_msg}")
        else:
            results["uploads"][platform_name] = {"status": "skipped", "reason": "Module not available"}
            results["platforms_skipped"].append(platform_name)

    print("\n" + "=" * 60)
    print("UPLOAD STATUS REPORT")
    print("=" * 60)
    report_order = [("FACEBOOK", "facebook"), ("INSTAGRAM", "instagram"), ("YOUTUBE", "youtube"),
                    ("TIKTOK", "tiktok"), ("THREADS", "threads"), ("TWITTER", "twitter"),
                    ("VK", "vk"), ("TELEGRAM", "telegram")]
    for pname, pkey in report_order:
        pinfo = results["uploads"].get(pkey, {})
        if pinfo and pinfo.get("status") in ("success", "published"):
            pid = pinfo.get("id", "N/A")
            link = pinfo.get("link") or pinfo.get("url") or pinfo.get("post_url") or ""
            if link:
                print(f"{pname}: SUCCESS (ID: {pid}) LINK: {link}")
            else:
                print(f"{pname}: SUCCESS (ID: {pid})")
        elif pinfo and pinfo.get("status") == "skipped":
            print(f"{pname}: SKIPPED")
        elif pinfo:
            err = str(pinfo.get("error", ""))[:80]
            print(f"{pname}: FAILED - {err}")
        else:
            pl = pkey.lower()
            failed = pl in [p.lower() for p in results.get("platforms_failed", [])]
            skipped = pl in [p.lower() for p in results.get("platforms_skipped", [])]
            print(f"{pname}: {'FAILED' if failed else ('SKIPPED' if skipped else '-')}")
    print("=" * 60)

    results_file = Path("output") / f"upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


def main():
    print("\n" + "=" * 80)
    print("AUTOMATED UPLOAD")
    print("=" * 80)

    reel = get_latest_reel()
    if not reel:
        print("\nNo reel found!")
        sys.exit(1)

    print(f"\nFound latest reel:")
    print(f"   Category: {reel['category']}")
    print(f"   Video: {reel['video_path']}")
    print(f"   Phrases: {len(reel['phrases'])}")

    video_title = get_video_title() or reel["category"]
    caption = generate_caption(reel['phrases'], reel['category'], platform="facebook")
    print(f"\nGenerated caption ({len(caption)} chars):")
    print("-" * 80)
    print(caption[:500] + "..." if len(caption) > 500 else caption)
    print("-" * 80)

    results = upload_to_all_platforms(reel['video_path'], caption, reel['category'], reel['phrases'], video_title)
    results["phrases"] = reel['phrases']

    successful = len(results.get("platforms_successful", []))
    failed = len(results.get("platforms_failed", []))
    skipped = len(results.get("platforms_skipped", []))

    if successful > 0:
        print(f"\nUpload complete! {successful} platform(s) successful.")
        if skipped > 0:
            print(f"{skipped} platform(s) skipped - add credentials to enable them")
        sys.exit(0)
    elif failed > 0:
        print(f"\nAll attempted uploads failed ({failed} failed, {skipped} skipped).")
        sys.exit(1)
    else:
        print(f"\nAll uploads skipped ({skipped} skipped).")
        sys.exit(1)


if __name__ == "__main__":
    main()
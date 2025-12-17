"""
Generate new Greek topics using AI when topics.txt runs low.

This script:
1. Checks if topics.txt has enough topics (< 500 remaining)
2. Generates 100 new unique Greek topics using Pollinations AI
3. Appends them to topics.txt
"""

import requests
from urllib.parse import quote
from pathlib import Path
import time
import re

def generate_new_topics(count=100):
    """Generate new Greek topics about ancient women with retry logic."""
    
    base_url = "https://text.pollinations.ai/"
    
    # Shorter, simpler prompt to avoid 400 errors
    prompt = f"Δημιούργησε {count} μοναδικά θέματα για γυναίκες στους αρχαίους πολιτισμούς"
    
    url = base_url + quote(prompt)
    params = {
        "model": "openai",
        "temperature": 0.9
    }
    
    print(f"[topics] Generating {count} new Greek topics...")
    
    # Retry logic with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, timeout=120)
            r.raise_for_status()
            
            # Parse topics
            topics = []
            for line in r.text.strip().split('\n'):
                # Remove numbering and clean
                cleaned = line.strip()
                # Remove common prefixes
                for prefix in ['- ', '* ', '• ', '→ ', '✓ ']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):]
                # Remove numbering like "1. " or "1) "
                cleaned = re.sub(r'^\d+[\.\:\)]\s*', '', cleaned)
                
                if cleaned and len(cleaned) > 5:
                    topics.append(cleaned)
            
            if len(topics) >= count // 2:  # Accept if we got at least half
                print(f"[topics] Successfully generated {len(topics)} topics!")
                return topics[:count]
            else:
                print(f"[topics] Only got {len(topics)} topics, retrying...")
                raise ValueError(f"Insufficient topics generated: {len(topics)}")
                
        except Exception as e:
            wait_time = (attempt + 1) * 5
            if attempt < max_retries - 1:
                print(f"[topics] Error: {e}")
                print(f"[topics] Retry {attempt + 1}/{max_retries} (waiting {wait_time}s)...")
                time.sleep(wait_time)
            else:
                print(f"[topics] Failed after {max_retries} attempts: {e}")
                raise
    
    return []

def check_and_update_topics():
    """Check topics.txt and verify it exists."""
    
    topics_file = Path('topics.txt')
    
    # Read existing topics
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    else:
        print("[topics] ERROR: topics.txt not found!")
        existing_topics = []
    
    print(f"[topics] Current topics: {len(existing_topics)}")
    
    # We have 600 pre-generated topics, so we don't need to generate more
    # Only generate if we're critically low (< 50 topics)
    if len(existing_topics) < 50:
        print(f"[topics] CRITICAL: Very low on topics! Attempting to generate more...")
        print(f"[topics] WARNING: Pollinations AI API is unreliable and may fail.")
        
        try:
            new_topics = generate_new_topics(100)
            
            # Append to file
            with open(topics_file, 'a', encoding='utf-8') as f:
                for topic in new_topics:
                    f.write(f"{topic}\n")
            
            print(f"[topics] Added {len(new_topics)} new Greek topics!")
            print(f"[topics] Total topics now: {len(existing_topics) + len(new_topics)}")
        except Exception as e:
            print(f"[topics] ERROR: Could not generate new topics: {e}")
            print(f"[topics] WARNING: Continuing with {len(existing_topics)} existing topics...")
            if len(existing_topics) == 0:
                print(f"[topics] FATAL: No topics available! Please check topics.txt file.")
                raise
    elif len(existing_topics) < 200:
        print(f"[topics] WARNING: Running low on topics ({len(existing_topics)} remaining)")
        print(f"[topics] Consider manually adding more topics to topics.txt")
    else:
        print(f"[topics] ✓ Sufficient topics available ({len(existing_topics)})")

if __name__ == '__main__':
    check_and_update_topics()

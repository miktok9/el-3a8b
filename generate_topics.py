"""
Generate new Greek topics using AI when topics.txt runs low.

This script:
1. Checks if topics.txt has enough topics (< 500 remaining)
2. Generates 100 new unique Greek topics using Pollinations AI paid API
3. Appends them to topics.txt
"""

import os
import requests
from urllib.parse import quote
from pathlib import Path
import time
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_new_topics(count=100):
    """Generate new Greek topics about ancient women using paid Pollinations API."""
    
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY environment variable is required for paid API")

    system = (
        "Είσαι ιστορικός ειδικευμένος στην ιστορία των γυναικών στους αρχαίους πολιτισμούς. "
        f"Δημιούργησε {count} μοναδικά θέματα στα ελληνικά. "
        "Κάθε θέμα πρέπει να είναι σύντομο (5-10 λέξεις), ενδιαφέρον και εκπαιδευτικό. "
        "Τα θέματα πρέπει να καλύπτουν: νόμους, έθιμα, διάσημες γυναίκες, επαγγέλματα, θρησκεία, κουλτούρα, τέχνη. "
        "ΓΡΑΨΕ ΜΟΝΟ τα θέματα, ένα ανά γραμμή, χωρίς αριθμούς και σύμβολα."
    )

    prompt = f"Γυναίκες στους αρχαίους πολιτισμούς {count} μοναδικά θέματα"

    url = f"https://gen.pollinations.ai/text/{quote(prompt)}"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "model": "nova-fast",
        "temperature": 0.9,
        "system": system,
        "json": False
    }
    
    print(f"[topics] Generating {count} new Greek topics...")
    r = requests.get(url, headers=headers, params=params, timeout=120)
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
    
    return topics[:count]

def check_and_update_topics():
    """Check topics.txt and add more if needed."""
    
    topics_file = Path('topics.txt')
    
    # Read existing topics
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    else:
        existing_topics = []
    
    print(f"[topics] Current topics: {len(existing_topics)}")
    
    # Check if we need more topics
    if len(existing_topics) < 50:
        print(f"[topics] Low on topics! Generating 100 more...")
        
        new_topics = generate_new_topics(100)
        
        # Append to file
        with open(topics_file, 'a', encoding='utf-8') as f:
            for topic in new_topics:
                f.write(f"{topic}\n")
        
        print(f"[topics] Added {len(new_topics)} new Greek topics!")
        print(f"[topics] Total topics now: {len(existing_topics) + len(new_topics)}")
    else:
        print(f"[topics] Enough topics available ({len(existing_topics)})")

if __name__ == '__main__':
    check_and_update_topics()

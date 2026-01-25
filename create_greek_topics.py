"""
Generate 600+ Greek topics about ancient women's history using Pollinations AI.
This script creates unique, engaging topics for the YouTube automation bot.
"""

import requests
from urllib.parse import quote
import time

def generate_greek_topics_batch(batch_num, batch_size=25):
    """Generate a batch of Greek topics."""
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY environment variable is required for paid API")
    
    # System prompt for Greek topics
    system = (
        "Είσαι ιστορικός που ειδικεύεται στην ιστορία των γυναικών στους αρχαίους πολιτισμούς. "
        f"Δημιούργησε {batch_size} μοναδικά θέματα στα ελληνικά για γυναίκες σε αρχαίους πολιτισμούς. "
        "Κάθε θέμα πρέπει να είναι 5-10 λέξεις, ενδιαφέρον και εκπαιδευτικό. "
        "Καλύπτει: νόμους, έθιμα, διάσημες γυναίκες, επαγγέλματα, θρησκεία, πολιτισμό, τέχνη. "
        "Εξάγει ΜΟΝΟ τα θέματα, ένα ανά γραμμή, χωρίς αριθμούς ή κουκκίδες."
    )
    
    prompt = f"Δημιούργησε {batch_size} μοναδικά ελληνικά θέματα για γυναίκες σε αρχαίους πολιτισμούς"
    
    url = f"https://gen.pollinations.ai/text/{quote(prompt)}"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "model": "nova-fast",
        "temperature": 0.9,
        "system": system,
        "json": False
    }
    
    max_retries = 3
    for retry in range(max_retries):
        try:
            print(f"  Batch {batch_num}: Requesting {batch_size} topics... (attempt {retry + 1})")
            r = requests.get(url, headers=headers, params=params, timeout=120)
            r.raise_for_status()
            
            text = r.text.strip()
            
            # Split into lines and clean
            topics = []
            for line in text.split('\n'):
                line = line.strip()
                # Remove numbering
                line = line.lstrip('0123456789.-*•) ')
                line = line.strip()
                if line and len(line) > 15:  # Ensure meaningful topics
                    topics.append(line)
            
            if topics:
                print(f"  ✓ Batch {batch_num}: Got {len(topics)} topics")
                return topics
            else:
                print(f"  ⚠ Batch {batch_num}: No topics extracted, retrying...")
                time.sleep(5)
                
        except Exception as e:
            print(f"  ✗ Batch {batch_num}: Error - {str(e)[:100]}")
            if retry < max_retries - 1:
                time.sleep(5)
    
    return []

def generate_all_topics(target=600):
    """Generate all topics with retries."""
    
    all_topics = []
    batch_size = 25
    max_batches = 30  # 30 batches * 25 = 750 topics (with buffer)
    
    print(f"Generating {target}+ Greek topics about ancient women's history...")
    print("=" * 60)
    
    for batch_num in range(1, max_batches + 1):
        if len(all_topics) >= target:
            print(f"\n✓ Target of {target} topics reached!")
            break
        
        topics = generate_greek_topics_batch(batch_num, batch_size)
        
        if topics:
            all_topics.extend(topics)
            print(f"  Total so far: {len(all_topics)}")
        
        # Rate limiting - wait between batches
        if batch_num < max_batches:
            time.sleep(4)
    
    return all_topics

def main():
    """Main function."""
    print("\nGreek Topics Generator for Ancient Women's History")
    print("=" * 60)
    
    # Generate topics
    topics = generate_all_topics(target=600)
    
    if not topics:
        print("\n❌ ERROR: No topics were generated!")
        print("Please check your internet connection and try again.")
        return
    
    # Remove duplicates while preserving order
    unique_topics = []
    seen = set()
    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower not in seen and len(topic) > 15:
            seen.add(topic_lower)
            unique_topics.append(topic)
    
    print("\n" + "=" * 60)
    print(f"📊 Statistics:")
    print(f"  Total generated: {len(topics)}")
    print(f"  Unique topics: {len(unique_topics)}")
    print(f"  Duplicates removed: {len(topics) - len(unique_topics)}")
    
    # Save to file
    with open("topics.txt", "w", encoding="utf-8") as f:
        for topic in unique_topics:
            f.write(f"{topic}\n")
    
    print(f"\n✅ Topics saved to topics.txt")
    print("=" * 60)
    print("✅ DONE! Greek topics ready for use.")
    print("=" * 60)

if __name__ == "__main__":
    main()

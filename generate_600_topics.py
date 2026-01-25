"""
Generate 600 Greek topics about ancient women's history.
"""

import requests
from urllib.parse import quote
from pathlib import Path
import time

def generate_greek_topics_batch(batch_num, count=100):
    """Generate a batch of Greek topics."""
    
    base_url = "https://text.pollinations.ai/"
    
    # Simpler system prompt
    system = (
        "Είσαι ιστορικός που ειδικεύεται στην ιστορία των γυναικών στους αρχαίους πολιτισμούς. "
        f"Δημιούργησε {count} μοναδικά θέματα στα ελληνικά για γυναίκες σε αρχαίους πολιτισμούς. "
        "Κάθε θέμα πρέπει να είναι 5-10 λέξεις, ενδιαφέρον και εκπαιδευτικό. "
        "Καλύπτει: νόμους, έθιμα, διάσημες γυναίκες, επαγγέλματα, θρησκεία, πολιτισμό, τέχνη. "
        "Εξάγει ΜΟΝΟ τα θέματα, ένα ανά γραμμή, χωρίς αριθμούς ή κουκκίδες."
    )
    
    prompt = f"Δημιούργησε {count} μοναδικά ελληνικά θέματα για γυναίκες σε αρχαίους πολιτισμούς"
    
    url = base_url + quote(prompt)
    params = {"model": "openai", "temperature": 0.9, "system": system}
    
    print(f"[batch {batch_num}] Generating {count} Greek topics...")
    
    try:
        r = requests.get(url, params=params, timeout=120)
        r.raise_for_status()
        
        # Parse topics
        topics = []
        for line in r.text.strip().split('\n'):
            cleaned = line.strip()
            # Remove common prefixes
            for prefix in ['- ', '* ', '• ', '→ ', '> ']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):]
            # Remove numbering
            import re
            cleaned = re.sub(r'^\d+[\.\:\)\-]\s*', '', cleaned)
            
            if cleaned and len(cleaned) > 5:
                topics.append(cleaned)
        
        print(f"[batch {batch_num}] Generated {len(topics)} topics")
        return topics[:count]
    
    except Exception as e:
        print(f"[batch {batch_num}] Error: {e}")
        return []

def main():
    """Generate 600 Greek topics in batches."""
    
    all_topics = []
    batches = 6  # 6 batches of 100 = 600 topics
    
    for i in range(batches):
        topics = generate_greek_topics_batch(i+1, 100)
        all_topics.extend(topics)
        
        print(f"[progress] Total topics so far: {len(all_topics)}")
        
        # Wait between batches to avoid rate limits
        if i < batches - 1:
            print("[progress] Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    # Write to file
    topics_file = Path('topics.txt')
    with open(topics_file, 'w', encoding='utf-8') as f:
        for topic in all_topics:
            f.write(f"{topic}\n")
    
    print(f"\n[done] Generated {len(all_topics)} Greek topics!")
    print(f"[done] Saved to {topics_file}")

if __name__ == '__main__':
    main()

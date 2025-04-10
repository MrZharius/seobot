# utils.py
from textblob import TextBlob
import re

def calculate_water(text):
    words = text.split()
    stop_words = set(['в', 'на', 'и', 'что', 'как', 'по', 'из', 'к', 'у', 'не', 'за', 'с', 'со', 'а', 'но', 'от'])
    if not words:
        return 0
    water = len([w for w in words if w.lower() in stop_words])
    return round((water / len(words)) * 100, 2)

def analyze_tone(text):
    blob = TextBlob(text)
    return round(blob.sentiment.polarity, 2)

def extract_lsi_phrases(text, top_n=5):
    words = re.findall(r'\w{5,}', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:top_n]]

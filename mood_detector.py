from transformers import pipeline

# Load pre-trained emotion detection model
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None  # avoids deprecated warning
)

def detect_mood_hf(text):
    result = emotion_classifier(text)[0]
    # Sort by score descending
    sorted_result = sorted(result, key=lambda x: x['score'], reverse=True)
    top_emotion = sorted_result[0]['label']
    return top_emotion

# Entry point for testing
if __name__ == "__main__":
    sample_text = "I'm really happy and overjoyed."
    mood = detect_mood_hf(sample_text)
    print(f"Mood detected: {mood}")

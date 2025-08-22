import subprocess
import time
from spotify_auth import create_spotify_client
from mood_detector import detect_mood_hf as detect_mood_text
from face_mood_detector import detect_mood_from_face_live  # Facial expression module

# Mood to Spotify search query map
mood_to_query = {
    "joy": "feel good",
    "sadness": "sad songs",
    "anger": "aggressive rock",
    "fear": "calm music",
    "love": "romantic songs",
    "surprise": "electronic",
    "disgust": "dark ambient",
    "neutral": "chill vibes"
}

def get_music_recommendations(mood, limit=5):
    sp = create_spotify_client()
    query = mood_to_query.get(mood.lower(), "chill")
    results = sp.search(q=query, type="track", limit=limit)

    songs = []
    for item in results['tracks']['items']:
        name = item['name']
        artist = item['artists'][0]['name']
        uri = item['uri']  # Use URI to open in desktop app
        songs.append({
            "name": name,
            "artist": artist,
            "uri": uri
        })
    return songs

# Pretty print banner
def print_banner(song, index):
    print("\n" + "=" * 50)
    print(f"🎵  Song {index}: {song['name']} by {song['artist']}")
    print(f"🔗  Spotify URI: {song['uri']}")
    print("=" * 50)

# Main interactive loop
if __name__ == "__main__":
    print("🎧 Welcome to Moodify — Your Mood-Based Music Recommender!")
    mode = input("🤖 Choose input method - Type [1] for Text Input, [2] for Facial Expression: ").strip()

    if mode == '1':
        user_input = input("🗣️  How are you feeling today?\n> ")
        detected_mood = detect_mood_text(user_input)
    elif mode == '2':
        print("📸 Please look at the camera for mood detection...")
        detected_mood = detect_mood_from_face_live()
    else:
        print("❌ Invalid input. Exiting.")
        exit()

    print(f"\n🔍 Detected Mood: {detected_mood}")

    recommendations = get_music_recommendations(detected_mood)

    for idx, song in enumerate(recommendations, 1):
        print_banner(song, idx)
        play = input("▶️  Do you want to play this song? (y/n): ").strip().lower()

        if play == 'y':
            try:
                # This command opens the track in the Spotify desktop app on Windows
                subprocess.run(["cmd", "/c", f"start spotify:track:{song['uri'].split(':')[-1]}"], shell=True)
                print("🎶 Opening in Spotify desktop app...")
                time.sleep(2)
                input("⏹️  Press Enter when you're done listening to this song...")
            except Exception as e:
                print(f"⚠️  Failed to open in Spotify desktop app: {e}")
        else:
            print("⏭️  Skipping to next song...")

        continue_choice = input("➡️  Do you want to continue to the next recommendation? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\n👋 Thanks for using Moodify. Have a musical day!")
            break

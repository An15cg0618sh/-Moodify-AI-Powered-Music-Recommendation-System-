from flask import Flask, render_template, request, redirect, url_for
from mood_detector import detect_mood_hf as detect_mood_text
from face_mood_detector import detect_mood_from_face_live
from music_recommender import get_music_recommendations
from flask import Response
from face_mood_detector import gen_frames


app = Flask(__name__)



@app.route('/')
def index():
    error = request.args.get("error")
    return render_template('index.html', error=error)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recommend', methods=['POST'])
def recommend():
    input_method = request.form.get('input_method')
    detected_mood = None
    
    # Face detection or text input
    if input_method == 'text':
        user_input = request.form.get('user_input')
        if not user_input:
            return redirect(url_for('index', error="Please enter a mood description."))
        detected_mood = detect_mood_text(user_input)
      
    # Face - based mood detection  
    elif input_method == 'face':
        detected_mood = detect_mood_from_face_live()
        if not detected_mood:
            return redirect(url_for('index', error="Could not detect mood from face. Please try again."))
    else:
        return redirect(url_for('index', error="Invalid input method"))
    
    #Handle mood detection result
    if not detected_mood:
        return redirect(url_for('index', error="No mood detected. Please try again."))
    
    # Get music recommendations based on detected mood
    
    recommendations = get_music_recommendations(detected_mood)
    return render_template('result.html', mood=detected_mood, songs=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
    
    

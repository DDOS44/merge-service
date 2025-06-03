from flask import Flask, request, send_file
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import os
import uuid

app = Flask(__name__)

@app.route("/merge", methods=["POST"])
def merge():
    body = request.files['body']
    text = request.files['text'].read().decode('utf-8')
    music = request.files['music']

    uid = str(uuid.uuid4())
    body_path = f"/tmp/{uid}_body.mp4"
    music_path = f"/tmp/{uid}_music.mp3"
    output_path = f"/tmp/{uid}_output.mp4"

    body.save(body_path)
    music.save(music_path)

    video = VideoFileClip(body_path)
    audio = AudioFileClip(music_path).subclip(0, video.duration)
    video = video.set_audio(audio)

    txt_clip = TextClip(text, fontsize=48, color='white', size=video.size).set_position('center').set_duration(video.duration)
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return send_file(output_path, mimetype="video/mp4")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)

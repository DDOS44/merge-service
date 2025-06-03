from flask import Flask, request, send_file, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import os
import uuid
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/merge", methods=["POST"])
def merge():
    try:
        # Validate input
        if 'body' not in request.files or 'music' not in request.files or 'text' not in request.files:
            return jsonify({"error": "Missing one or more required files: body, music, text"}), 400

        body = request.files['body']
        text = request.files['text'].read().decode('utf-8')
        music = request.files['music']

        uid = str(uuid.uuid4())
        body_path = f"/tmp/{uid}_body.mp4"
        music_path = f"/tmp/{uid}_music.mp3"
        output_path = f"/tmp/{uid}_output.mp4"

        # Save files to disk
        body.save(body_path)
        music.save(music_path)

        logging.info(f"Files saved: {body_path}, {music_path}")

        # Load clips
        video = VideoFileClip(body_path)
        audio = AudioFileClip(music_path).subclip(0, video.duration)
        video = video.set_audio(audio)

        # Add text overlay
        txt_clip = TextClip(text, fontsize=48, color='white', size=video.size).set_position('center').set_duration(video.duration)

        final = CompositeVideoClip([video, txt_clip])

        # Write output video file
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

        logging.info(f"Video created at {output_path}")

        # Cleanup input files
        os.remove(body_path)
        os.remove(music_path)

        # Serve output file
        return send_file(output_path, mimetype="video/mp4", as_attachment=True)

    except Exception as e:
        logging.error(f"Error in merge endpoint: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Attempt cleanup of output file if exists
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as cleanup_err:
            logging.warning(f"Cleanup failed: {cleanup_err}")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)

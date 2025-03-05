from flask import Flask, render_template, request, jsonify, send_file
import http.client
import json
import os
import yt_dlp
import threading
import time
import re

app = Flask(__name__)

# Folders for downloads
WEBM_FOLDER = "RECOMMEND_DOWNLOAD"
MP3_FOLDER = "downloads"
ZIP_FILE = "downloads.zip"

# YouTube API setup (Hardcoded as per request)
API_HOST = "youtube-v31.p.rapidapi.com"
API_KEY = "56dfead9d0msh16dd2994a8f600dp12c061jsn103a13978d3f"

# Regex to extract video ID
YOUTUBE_REGEX = re.compile(r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})")

# Ensure directories exist
os.makedirs(WEBM_FOLDER, exist_ok=True)
os.makedirs(MP3_FOLDER, exist_ok=True)

def extract_video_id(youtube_url):
    """Extracts video ID from YouTube URL"""
    match = YOUTUBE_REGEX.match(youtube_url)
    return match.group(1) if match else None

def get_related_videos(video_id, max_results=5):
    """Fetch related YouTube videos"""
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
        conn.request("GET", f"/search?relatedToVideoId={video_id}&part=id,snippet&type=video&maxResults={max_results}", headers=headers)
        res = conn.getresponse()

        if res.status != 200:
            return []

        data = json.loads(res.read().decode("utf-8"))
        return [{
            "title": sanitize_filename(item["snippet"]["title"]),
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "id": item['id']['videoId']
        } for item in data.get("items", [])]
    except Exception as e:
        print(f"Error fetching related videos: {e}")
        return []

def sanitize_filename(title):
    """Removes invalid filename characters from a video title."""
    return re.sub(r'[\\/*?:"<>|]', "", title)  # Removes special characters

def download_webm(youtube_url, video_title):
    """Downloads a YouTube video's audio in .webm format with a sanitized title."""
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(WEBM_FOLDER, f"{video_title}.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print(f"Downloaded: {youtube_url} as {video_title}.webm")
    except Exception as e:
        print(f"Error downloading {youtube_url}: {e}")

def start_background_download(video_list):
    """Starts downloading all related videos in the background"""
    for video in video_list:
        download_webm(video["url"], video["title"])
        time.sleep(1)  # Small delay to prevent system overload

@app.route("/")
def index():
    """Render HTML page"""
    return render_template("index.html")

@app.route("/get_videos", methods=["POST"])
def get_videos():
    """Fetch related videos and start background downloads"""
    youtube_url = request.form.get("video_id")
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    videos = get_related_videos(video_id)
    threading.Thread(target=start_background_download, args=(videos,), daemon=True).start()
    return jsonify(videos)

@app.route("/list_audio")
def list_audio():
    """Returns a list of available .webm files"""
    files = [f for f in os.listdir(WEBM_FOLDER) if f.endswith(".webm")]
    return jsonify(files)

@app.route("/stream_audio/<filename>")
def stream_audio(filename):
    """Streams an audio file"""
    file_path = os.path.join(WEBM_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="audio/webm", as_attachment=False)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
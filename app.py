from flask import Flask, send_from_directory, render_template_string
import os
import re
from datetime import datetime

app = Flask(__name__)

IMAGE_FOLDER = "/mnt/bygg"

# Regex to extract timestamp from filename (image_YYYYMMDD_HHMMSS.jpg)
timestamp_re = re.compile(r'image_(\d{8}_\d{6})')

def get_timestamp(filename):
    match = timestamp_re.search(filename)
    if not match:
        return datetime.min
    try:
        return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.min

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>St. Olav Byggeprosjekt</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f4f4;
      color: #333;
      text-align: center;
      padding: 2em;
    }
    .carousel-container {
      display: inline-block;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.1);
      padding: 2em;
      max-width: 90%;
    }
    img {
      max-width: 100%;
      max-height: 500px;
      border-radius: 8px;
    }
    button {
      margin: 1em;
      padding: 0.6em 1.4em;
      font-size: 1.1em;
      border: none;
      background-color: #3498db;
      color: white;
      border-radius: 8px;
      cursor: pointer;
    }
    button:hover {
      background-color: #2980b9;
    }
    .download-link, #filename-display {
      margin-top: 1em;
      display: block;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>Bilde Karusell</h1>
  <div class="carousel-container">
    <img id="carousel-image" src="" alt="No images found" />
    <p id="filename-display"></p>
    <a id="download-link" class="download-link" href="" download>Last ned dette bilde</a>
    <div>
      <button onclick="prevImage()">( Eldre )</button>
      <button onclick="nextImage()">( Nyere )</button>
    </div>
  </div>

  <script>
    let images = {{ images | tojson }};
    let index = 0;

    function updateImage() {
      if (images.length === 0) {
        document.getElementById('carousel-image').alt = "No images available";
        document.getElementById('carousel-image').src = "";
        document.getElementById('download-link').style.display = 'none';
        document.getElementById('filename-display').textContent = "";
        return;
      }
      let filename = images[index];
      document.getElementById('carousel-image').src = '/images/' + filename;
      document.getElementById('download-link').href = '/images/' + filename;
      document.getElementById('download-link').style.display = 'inline-block';
      document.getElementById('filename-display').textContent = filename;
    }

    function prevImage() {
      index = (index + 1) % images.length; // older
      updateImage();
    }

    function nextImage() {
      index = (index - 1 + images.length) % images.length; // newer
      updateImage();
    }

    updateImage();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    try:
        files = [
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))
        ]
        files.sort(key=get_timestamp, reverse=True)
    except Exception as e:
        files = []

    return render_template_string(HTML_TEMPLATE, images=files)

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, send_from_directory, render_template_string, request
import os
import re
from datetime import datetime, timedelta

app = Flask(__name__)

IMAGE_FOLDER = "/mnt/bygg"
timestamp_re = re.compile(r'image_(\d{8}_\d{6})')

def get_timestamp(filename):
    match = timestamp_re.search(filename)
    if not match:
        return datetime.min
    try:
        return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.min

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Fancy Image Carousel</title>
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
    .nav-links {
      margin-top: 2em;
    }
    .nav-links a {
      margin: 0 1em;
      text-decoration: none;
      font-weight: bold;
      color: #3498db;
    }
  </style>
</head>
<body>
  <h1>Bilde Karusell</h1>
  <div class="carousel-container">
    <img id="carousel-image" src="" alt="No images found" />
    <p id="filename-display"></p>
    <a id="download-link" class="download-link" href="" download>Last ned dette Bilde</a>
    <div>
      <button onclick="nextImage()">⟨ Nyere</button>
      <button onclick="prevImage()">Eldre ⟩</button>
    </div>
  </div>
  <div class="nav-links">
    {% if offset > 0 %}
    <a href="/?offset={{ offset - 1 }}">⟵ One hour newer</a>
    {% endif %}
    <a href="/?offset={{ offset + 1 }}">One hour older ⟶</a>
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
      index = (index + 1) % images.length;
      updateImage();
    }

    function nextImage() {
      index = (index - 1 + images.length) % images.length;
      updateImage();
    }

    updateImage();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    offset = int(request.args.get("offset", 0))

    try:
        all_files = [
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))
        ]
        all_files = sorted(all_files, key=get_timestamp, reverse=True)

        # Filtrer basert på offset timer
        now = datetime.now()
        from_time = now - timedelta(hours=offset + 1)
        to_time = now - timedelta(hours=offset)
        filtered = [
            f for f in all_files
            if from_time <= get_timestamp(f) < to_time
        ][:168]  # maks 48 bilder

    except Exception as e:
        filtered = []

    return render_template_string(HTML_TEMPLATE, images=filtered, offset=offset)

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

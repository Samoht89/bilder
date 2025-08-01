from flask import Flask, send_from_directory, render_template_string
import os
import re
from datetime import datetime

app = Flask(__name__)
IMAGE_FOLDER = "/mnt/bygg"

# Regex for å hente ut timestamp fra filnavn
timestamp_re = re.compile(r'image_(\d{8}_\d{6})')

def get_timestamp(filename):
    match = timestamp_re.search(filename)
    if not match:
        return datetime.min
    try:
        return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
    except ValueError:
        return datetime.min

def format_timestamp(ts):
    try:
        months = [
            "januar", "februar", "mars", "april", "mai", "juni",
            "juli", "august", "september", "oktober", "november", "desember"
        ]
        return {
            "date": f"{ts.day}. {months[ts.month - 1]} {ts.year}",
            "time": ts.strftime("%H:%M:%S")
        }
    except Exception:
        return {"date": "", "time": ""}

# Hovedside med karusell
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Bildekarusell</title>
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
    .nav-link {
      display: block;
      margin-top: 1.5em;
    }
  </style>
</head>
<body>
  <h1>Bildekarusell</h1>
  <div class="carousel-container">
    <img id="carousel-image" src="" alt="Ingen bilder funnet" />
    <p id="filename-display"></p>
    <a id="download-link" class="download-link" href="" download>Last ned bilde</a>
    <div>
      <button onclick="prevImage()">Eldre ⟩</button>
      <button onclick="nextImage()">⟨ Nyere</button>
    </div>
  </div>
  <a href="/gallery" class="nav-link">Gå til galleri</a>

  <script>
    let images = {{ images | tojson }};
    let index = 0;

    function updateImage() {
      if (images.length === 0) {
        document.getElementById('carousel-image').alt = "Ingen bilder";
        document.getElementById('carousel-image').src = "";
        document.getElementById('download-link').style.display = 'none';
        document.getElementById('filename-display').textContent = "";
        return;
      }
      let img = images[index];
      document.getElementById('carousel-image').src = '/images/' + img.filename;
      document.getElementById('download-link').href = '/images/' + img.filename;
      document.getElementById('download-link').style.display = 'inline-block';
      document.getElementById('filename-display').textContent = img.date + ' - ' + img.time;
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

# Galleriside
GALLERY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Bildegalleri</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f0f0f0;
      padding: 2em;
    }
    h1 {
      text-align: center;
    }
    .controls {
      text-align: center;
      margin-bottom: 2em;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1em;
    }
    .card {
      background: #fff;
      border-radius: 8px;
      padding: 1em;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
      text-align: center;
      position: relative;
    }
    .card img {
      max-width: 100%;
      max-height: 150px;
      border-radius: 4px;
      transition: transform 0.2s;
      cursor: zoom-in;
    }
    .card img:hover {
      transform: scale(1.05);
    }
    .timestamp {
      margin-top: 0.5em;
      font-size: 0.9em;
      color: #555;
    }
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      padding-top: 60px;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      overflow: auto;
      background-color: rgba(0,0,0,0.8);
    }
    .modal-content {
      margin: auto;
      display: block;
      max-width: 90%;
      max-height: 80vh;
    }
    .close {
      position: absolute;
      top: 20px;
      right: 35px;
      color: white;
      font-size: 40px;
      font-weight: bold;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1>📁 Bildegalleri</h1>
  <div class="controls">
    <label for="datePicker">Filtrer etter dato:</label>
    <input type="date" id="datePicker" onchange="filterByDate()">
  </div>
  <div class="grid" id="imageGrid">
    {% for img in images %}
    <div class="card" data-date="{{ img.date_iso }}">
      <img src="/images/{{ img.filename }}" alt="image" onclick="openModal(this.src)">
      <div class="timestamp">{{ img.date }}<br>{{ img.time }}</div>
    </div>
    {% endfor %}
  </div>
  <div id="myModal" class="modal" onclick="closeModal()">
    <span class="close" onclick="closeModal()">&times;</span>
    <img class="modal-content" id="modalImage">
  </div>
  <script>
    function openModal(src) {
      document.getElementById("myModal").style.display = "block";
      document.getElementById("modalImage").src = src;
    }

    function closeModal() {
      document.getElementById("myModal").style.display = "none";
    }

    function filterByDate() {
      const selected = document.getElementById("datePicker").value;
      const cards = document.querySelectorAll(".card");
      cards.forEach(card => {
        if (!selected || card.dataset.date === selected) {
          card.style.display = "";
        } else {
          card.style.display = "none";
        }
      });
    }
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

        images = []
        for f in files:
            ts = get_timestamp(f)
            formatted = format_timestamp(ts)
            images.append({
                "filename": f,
                "date": formatted["date"],
                "time": formatted["time"]
            })
    except Exception:
        images = []
    return render_template_string(HTML_TEMPLATE, images=images)

@app.route("/gallery")
def gallery():
    try:
        files = [
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))
        ]
        files.sort(key=get_timestamp, reverse=True)

        images = []
        for f in files[:150]:  # vis de nyeste 150
            ts = get_timestamp(f)
            formatted = format_timestamp(ts)
            images.append({
                "filename": f,
                "date": formatted["date"],
                "time": formatted["time"],
                "date_iso": ts.strftime("%Y-%m-%d")
            })
    except Exception:
        images = []
    return render_template_string(GALLERY_TEMPLATE, images=images)

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

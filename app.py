from flask import Flask, send_from_directory, jsonify, render_template_string
import os

app = Flask(__name__)

IMAGE_FOLDER = "/mnt/bygg"

# Basic HTML template with a simple image wheel and download links
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Image Carousel</title>
<style>
  body { font-family: Arial, sans-serif; text-align: center; margin: 2em; }
  img { max-width: 600px; max-height: 400px; }
  .carousel-container { position: relative; display: inline-block; }
  button { margin: 1em; padding: 0.5em 1em; font-size: 1em; }
  a.download-link { display: block; margin-top: 1em; }
</style>
</head>
<body>
  <h1>Image Carousel</h1>
  <div class="carousel-container">
    <img id="carousel-image" src="" alt="No images found" />
  </div>
  <br/>
  <button onclick="prevImage()">Prev</button>
  <button onclick="nextImage()">Next</button>
  <a id="download-link" class="download-link" href="" download>Download This Image</a>

  <script>
    let images = {{ images | tojson }};
    let index = 0;

    function updateImage() {
      if(images.length === 0) {
        document.getElementById('carousel-image').alt = "No images available";
        document.getElementById('carousel-image').src = "";
        document.getElementById('download-link').style.display = 'none';
        return;
      }
      document.getElementById('carousel-image').src = '/images/' + images[index];
      document.getElementById('download-link').href = '/images/' + images[index];
      document.getElementById('download-link').style.display = 'inline-block';
    }

    function prevImage() {
      index = (index - 1 + images.length) % images.length;
      updateImage();
    }

    function nextImage() {
      index = (index + 1) % images.length;
      updateImage();
    }

    updateImage();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    # List image files in IMAGE_FOLDER
    try:
        files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    except Exception as e:
        files = []
    return render_template_string(HTML_TEMPLATE, images=files)

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

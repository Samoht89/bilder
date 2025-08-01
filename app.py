from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

IMAGE_FOLDER = "/mnt/bygg"

# Enhanced HTML template with a fancier image carousel and filename display
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Image Carousel</title>
<style>
  body { font-family: Arial, sans-serif; text-align: center; margin: 2em; }
  .carousel-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
  }
  img {
    max-width: 600px;
    max-height: 400px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }
  .filename {
    font-size: 1.2em;
    font-weight: bold;
    width: 200px;
    text-align: left;
  }
  button {
    margin: 1em;
    padding: 0.5em 1em;
    font-size: 1em;
    cursor: pointer;
  }
  a.download-link {
    display: block;
    margin-top: 1em;
    text-decoration: none;
    color: #007bff;
    font-weight: bold;
  }
  a.download-link:hover {
    text-decoration: underline;
  }
</style>
</head>
<body>
  <h1>Image Carousel</h1>
  <div class="carousel-container">
    <img id="carousel-image" src="" alt="No images found" />
    <div class="filename" id="filename-display">No images</div>
  </div>
  <button onclick="prevImage()">← Prev</button>
  <button onclick="nextImage()">Next →</button>
  <a id="download-link" class="download-link" href="" download>Download This Image</a>

  <script>
    let images = {{ images | tojson }};
    let index = 0;

    function updateImage() {
      if(images.length === 0) {
        document.getElementById('carousel-image').alt = "No images available";
        document.getElementById('carousel-image').src = "";
        document.getElementById('filename-display').textContent = "No images";
        document.getElementById('download-link').style.display = 'none';
        return;
      }
      const currentImage = images[index];
      document.getElementById('carousel-image').src = '/images/' + currentImage;
      document.getElementById('carousel-image').alt = currentImage;
      document.getElementById('filename-display').textContent = currentImage;
      document.getElementById('download-link').href = '/images/' + currentImage;
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
    try:
        files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    except Exception:
        files = []
    return render_template_string(HTML_TEMPLATE, images=files)

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

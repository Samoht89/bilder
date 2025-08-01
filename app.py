
from flask import Flask, send_from_directory, render_template, request
import os

app = Flask(__name__)
IMAGE_FOLDER = '/mnt/bygg'

@app.route('/')
def index():
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return render_template('index.html', images=images)

@app.route('/images/<path:filename>')
def serve_image(filename):
    as_attachment = request.args.get("download") == "1"
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=as_attachment)

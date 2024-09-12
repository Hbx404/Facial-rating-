from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

FACE_API_URL = 'https://api-us.faceplusplus.com/facepp/v3/detect'
API_KEY = os.getenv('FACE_API_KEY')
API_SECRET = os.getenv('FACE_API_SECRET')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        files = {
            'api_key': (None, API_KEY),
            'api_secret': (None, API_SECRET),
            'image_file': open(file_path, 'rb'),
            'return_attributes': (None, 'age,gender,smile,emotion')
        }

        response = requests.post(FACE_API_URL, files=files)
        data = response.json()

        faces = data.get('faces', [])
        if faces:
            face_attributes = faces[0]['attributes']
            ratings = {
                'age': face_attributes['age']['value'],
                'gender': face_attributes['gender']['value'],
                'smile': face_attributes['smile']['value'],
                'emotion': face_attributes['emotion']
            }
            return jsonify(ratings)
        else:
            return jsonify({"error": "No face detected."}), 400

    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
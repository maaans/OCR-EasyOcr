import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import easyocr

# Inisialisasi EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)  # Set GPU=False jika tidak menggunakan GPU

# Set direktori untuk menyimpan file yang di-upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
FILE_DIR = 'files'

# Inisialisasi Flask app
app = Flask(__name__)

# Buat direktori jika belum ada
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

# Fungsi untuk memeriksa file yang di-upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rute untuk upload file dan melakukan OCR
@app.route('/easyocr', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = os.path.join(FILE_DIR, secure_filename(file.filename))
        file.save(filename)
        
        # Proses OCR dengan EasyOCR
        try:
            parsed = reader.readtext(filename, detail=1)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        # Struktur output seperti yang diminta
        output = {
            "data": []
        }
        
        for (bbox, text, confidence) in parsed:
            # Bounding box coordinates
            (top_left, top_right, bottom_right, bottom_left) = bbox
            
            # Bounding box in terms of left, top, width, and height
            ########################
            # fill with your bounding box

            # Menyusun data sesuai format yang diinginkan
            ocr_result = {
                "bbox": {
                    "BoundingBox": {
                        "Height": height,
                        "Left": left,
                        "Top": top,
                        "Width": width
                    },
                    "Polygon": [
                        {"X": float(top_left[0]), "Y": float(top_left[1])},
                        {"X": float(top_right[0]), "Y": float(top_right[1])},
                        {"X": float(bottom_right[0]), "Y": float(bottom_right[1])},
                        {"X": float(bottom_left[0]), "Y": float(bottom_left[1])}
                    ]
                },
                "confidence": float(confidence),  # Ensure it's a float
                "text": text,
                "type": "LINE"  # Anda bisa menyesuaikan ini sesuai konteks yang diinginkan
            }

            output["data"].append(ocr_result)
        
        # Kembalikan hasil dalam format JSON
        return jsonify(output)

    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)

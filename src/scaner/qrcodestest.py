from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import qrcode
import os
from io import BytesIO
from PIL import Image
import base64
import uuid

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/generate_qr": {"origins": "http://localhost:5173"}})

DB_PATH = '/Users/firdovsirzaev/Desktop/DigiMealFull/sampleDigiMeal/scaner/usertestpagedb.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id TEXT PRIMARY KEY,
            image BLOB,
            status INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()


init_db()

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    unique_id = str(uuid.uuid4())
    qr_image = generate_qr_code(unique_id)

    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO qr_codes (id, image, status) VALUES (?, ?, ?)',
                   (unique_id, qr_image, 1))
    conn.commit()
    conn.close()

    return jsonify({"id": unique_id, "image": qr_image, "status": 1}), 201

@app.route('/get_qrs', methods=['GET'])
def get_qrs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, image, status FROM qr_codes')
    rows = cursor.fetchall()
    conn.close()

    qr_data = [{"id": row[0], "image": row[1], "status": row[2]} for row in rows]
    return jsonify(qr_data), 200

@app.route('/update_status/<qr_id>', methods=['PATCH'])
def update_status(qr_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE qr_codes SET status = 0 WHERE id = ?', (qr_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated successfully"}), 200


# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)

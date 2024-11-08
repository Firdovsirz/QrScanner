from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# CORS is configured to allow all origins
CORS(app, resources={r"/update_status": {"origins": "*"}})

DB_PATH = os.path.join('/tmp', 'usertestpagedb.db')


# Initialize the database and table
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id TEXT PRIMARY KEY,
            image BLOB,
            status INTEGER
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/update_status', methods=['POST'])
def update_status():
    # Check if the incoming request is JSON
    if request.is_json:
        data = request.json
        qr_id = data.get('id')

        if not qr_id:
            return jsonify({"message": "QR ID is required"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query the database to find the QR ID with status 1
        cursor.execute("SELECT * FROM qr_codes WHERE id = ? AND status = 1", (qr_id,))
        result = cursor.fetchone()

        if result:
            # Update the status to 0 if the QR ID is found with status 1
            cursor.execute("UPDATE qr_codes SET status = 0 WHERE id = ?", (qr_id,))
            conn.commit()
            message = f"Status for QR ID {qr_id} updated to 0."
        else:
            message = f"No matching QR ID {qr_id} with status 1 found."

        conn.close()
        return jsonify({"message": message})
    else:
        # Handle case where the request is not JSON
        return jsonify({"message": "Request must be JSON"}), 400


if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
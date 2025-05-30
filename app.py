from flask import Flask, request, jsonify, render_template
from blockchain import Blockchain
from database import init_db, insert_file_record, insert_patient_record
from werkzeug.utils import secure_filename
import os
import hashlib
import datetime
import json

# --- App and Blockchain Setup ---
app = Flask(__name__)
blockchain = Blockchain()

# --- Initialize Database ---
init_db()

# --- Upload Folder Configuration ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper: Hash File Contents for IPFS Simulation ---
def hash_file_contents(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# --- UI Route ---
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# --- Route: Get the Blockchain ---
@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({
        "length": len(blockchain.chain),
        "chain": blockchain.to_dict()
    }), 200

# --- Route: Add a JSON Record to Blockchain & DB ---
@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.get_json()
    if not data or 'patient_id' not in data or 'record' not in data:
        return jsonify({"error": "Invalid data"}), 400

    # Compute hash of the record payload
    record_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    block_data = {
        'patient_id': data['patient_id'],
        'record': data['record'],
        'record_hash': record_hash,
        'timestamp': str(datetime.datetime.utcnow())
    }

    # Add to blockchain
    blockchain.add_block(block_data)
    # Persist to DB
    insert_patient_record(data['patient_id'], data['record'], record_hash)

    return jsonify({"message": "Record added to blockchain and database"}), 201

# --- Route: Upload File, Hash It, Add to Blockchain & DB ---
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Hash file content to simulate IPFS
    ipfs_hash = hash_file_contents(filepath)
    timestamp = str(datetime.datetime.utcnow())
    block_data = {
        'patient_id': "",            
        'file_name': filename,
        'ipfs_hash': ipfs_hash,
        'timestamp': timestamp
    }

    # Add to blockchain
    blockchain.add_block(block_data)
    # Persist to DB
    insert_file_record("", filename, ipfs_hash)

    return jsonify({
        'message': 'File uploaded and added to blockchain & database',
        'ipfs_hash': ipfs_hash
    }), 201

if __name__ == '__main__':
    app.run(debug=True)

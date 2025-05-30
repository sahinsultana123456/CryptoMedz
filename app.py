from flask import Flask, request, jsonify
from blockchain import Blockchain
from werkzeug.utils import secure_filename
import os
import hashlib
import datetime

app = Flask(__name__)
blockchain = Blockchain()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def hash_file_contents(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = blockchain.to_dict()
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data
    }), 200

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.get_json()
    if not data or 'patient_id' not in data or 'record' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    blockchain.add_block(data)
    return jsonify({"message": "Record added to blockchain"}), 201

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

    # Hash file content to simulate IPFS hash
    ipfs_like_hash = hash_file_contents(filepath)

    # Add file hash to blockchain with metadata
    data = {
        'file_name': filename,
        'ipfs_hash': ipfs_like_hash,
        'timestamp': str(datetime.datetime.utcnow())
    }
    blockchain.add_block(data)


    return jsonify({'message': 'File uploaded and added to blockchain', 'ipfs_hash': ipfs_like_hash}), 201

if __name__ == '__main__':
    app.run(debug=True)

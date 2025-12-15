from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# --------------------------
# File paths
# --------------------------
DATA_FILE = "patients.json"
UPLOAD_FOLDER = "Uploads"

# Create uploads folder if missing
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --------------------------
# Helper Functions
# --------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --------------------------
# Home
# --------------------------
@app.route("/")
def home():
    return "Backend Running OK"


# --------------------------
# Add / Update Patient
# --------------------------
@app.route("/add_patient", methods=["POST"])
def add_patient():
    data = load_data()
    incoming = request.get_json()

    pid = incoming.get("id")
    if not pid:
        return jsonify({"message": "Patient ID required"}), 400

    data[pid] = {
        "id": pid,
        "name": incoming.get("name", ""),
        "age": incoming.get("age", ""),
        "gender": incoming.get("gender", ""),
        "disease": incoming.get("disease", "")
    }

    save_data(data)
    return jsonify({"message": "Patient saved successfully!"})


# --------------------------
# Search Patient
# --------------------------
@app.route("/search_patient")
def search_patient():
    pid = request.args.get("id")
    data = load_data()

    if pid not in data:
        return jsonify({"message": "Not found"}), 404

    return jsonify(data[pid])


# --------------------------
# Delete Patient
# --------------------------
@app.route("/delete_patient", methods=["DELETE"])
def delete_patient():
    pid = request.args.get("id")
    data = load_data()

    if pid not in data:
        return jsonify({"message": "Patient not found"}), 404

    # Remove from JSON
    del data[pid]
    save_data(data)

    # Remove folder
    patient_dir = os.path.join(UPLOAD_FOLDER, pid)
    if os.path.exists(patient_dir):
        for file in os.listdir(patient_dir):
            os.remove(os.path.join(patient_dir, file))
        os.rmdir(patient_dir)

    return jsonify({"message": "Patient deleted successfully"})


# --------------------------
# Upload Report
# --------------------------
@app.route("/upload_report", methods=["POST"])
def upload_report():
    pid = request.form.get("id")
    file = request.files.get("file")

    if not pid:
        return jsonify({"message": "ID required"}), 400
    if not file:
        return jsonify({"message": "No file uploaded"}), 400

    patient_dir = os.path.join(UPLOAD_FOLDER, pid)
    if not os.path.exists(patient_dir):
        os.makedirs(patient_dir)

    path = os.path.join(patient_dir, file.filename)
    file.save(path)

    return jsonify({"message": "File uploaded successfully"})


# --------------------------
# List Reports
# --------------------------
@app.route("/list_reports")
def list_reports():
    pid = request.args.get("id")
    patient_dir = os.path.join(UPLOAD_FOLDER, pid)

    if not os.path.exists(patient_dir):
        return jsonify({"files": []})

    files = os.listdir(patient_dir)
    return jsonify({"files": files})


# --------------------------
# Get / View Report
# --------------------------
@app.route("/get_report")
def get_report():
    pid = request.args.get("id")
    filename = request.args.get("file")

    patient_dir = os.path.join(UPLOAD_FOLDER, pid)

    if not os.path.exists(os.path.join(patient_dir, filename)):
        return "File not found", 404

    return send_from_directory(patient_dir, filename)


# --------------------------
# Delete a Report
# --------------------------
@app.route("/delete_report", methods=["DELETE"])
def delete_report():
    pid = request.args.get("id")
    filename = request.args.get("file")

    patient_dir = os.path.join(UPLOAD_FOLDER, pid)
    file_path = os.path.join(patient_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    os.remove(file_path)
    return jsonify({"message": "Report deleted successfully"})


# --------------------------
# Run Server
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)

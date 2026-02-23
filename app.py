"""
Flask backend for network anomaly classification.
Loads the .pkl model (or trains from CSV if missing) and exposes a /predict API.
"""
import os
import pickle
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__, static_folder=".")

# Feature names in same order as training
FEATURE_NAMES = [
    "Inbound Rate(bit/s)",
    "Outbound Rate(bit/s)",
    "Inbound Bandwidth Utilization(%)",
    "Outbound Bandwidth Utilization(%)",
]
# Short keys expected from frontend
INPUT_KEYS = ["inbound_rate", "outbound_rate", "inbound_util", "outbound_util"]

MODEL_FILENAME = "network_anomaly_model.pkl"
CSV_FILENAME = "networkanomalydataset.csv"


def get_model_path():
    """Resolve path to .pkl: current dir first, then parent."""
    base = os.path.dirname(os.path.abspath(__file__))
    for folder in (base, os.path.dirname(base)):
        path = os.path.join(folder, MODEL_FILENAME)
        if os.path.isfile(path):
            return path
    return os.path.join(base, MODEL_FILENAME)


def get_csv_path():
    """Resolve path to CSV: current dir first, then parent."""
    base = os.path.dirname(os.path.abspath(__file__))
    for folder in (base, os.path.dirname(base)):
        path = os.path.join(folder, CSV_FILENAME)
        if os.path.isfile(path):
            return path
    return None


def load_or_train_model():
    """Load existing .pkl or train from CSV and save."""
    path = get_model_path()
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    csv_path = get_csv_path()
    if not csv_path:
        raise FileNotFoundError(
            f"Neither {MODEL_FILENAME} nor {CSV_FILENAME} found. "
            "Train the model first (e.g. run training.py) or add the CSV."
        )
    df = pd.read_csv(csv_path)
    X = df[FEATURE_NAMES]
    y = df["Label"]
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X, y)
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), MODEL_FILENAME)
    with open(save_path, "wb") as f:
        pickle.dump(clf, f)
    return clf


# Load model at startup (or train if missing)
try:
    model = load_or_train_model()
except Exception as e:
    model = None
    print(f"Warning: Could not load/train model: {e}. /predict will fail until fixed.")


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


@app.route("/api/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Add model or CSV and restart."}), 503
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    try:
        values = [float(data.get(k)) for k in INPUT_KEYS]
    except (TypeError, KeyError) as e:
        return jsonify({
            "error": "Invalid input. Send: inbound_rate, outbound_rate, inbound_util, outbound_util (numbers).",
            "detail": str(e),
        }), 400
    X = pd.DataFrame([values], columns=FEATURE_NAMES)
    pred = int(model.predict(X)[0])
    label = "Anomaly" if pred == 1 else "Normal"
    return jsonify({
        "prediction": pred,
        "label": label,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

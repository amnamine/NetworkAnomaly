"""
One-time test: send every row of the dataset to the website API and compare
predictions to actual labels. Does NOT modify index.html, styles.css, script.js, or app.py.
"""
import json
import urllib.request
import pandas as pd

API_URL = "http://127.0.0.1:5000/api/predict"
CSV_PATH = "networkanomalydataset.csv"
INPUT_KEYS = ["inbound_rate", "outbound_rate", "inbound_util", "outbound_util"]
COLUMNS = [
    "Inbound Rate(bit/s)",
    "Outbound Rate(bit/s)",
    "Inbound Bandwidth Utilization(%)",
    "Outbound Bandwidth Utilization(%)",
]

def main():
    df = pd.read_csv(CSV_PATH)
    total = len(df)
    correct = 0
    errors = []

    for i, row in df.iterrows():
        payload = {k: float(row[col]) for k, col in zip(INPUT_KEYS, COLUMNS)}
        true_label = int(row["Label"])
        try:
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            pred = int(data["prediction"])
            if pred == true_label:
                correct += 1
            else:
                errors.append((i + 2, true_label, pred, list(payload.values())))
        except Exception as e:
            errors.append((i + 2, true_label, None, str(e)))

    print(f"Total rows tested: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {100 * correct / total:.2f}%")
    if errors:
        print(f"\nMismatches/errors (first 20):")
        for item in errors[:20]:
            print(f"  Row {item[0]}: true={item[1]}, pred={item[2]}, payload/err={item[3]}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
    else:
        print("\nAll predictions matched the dataset labels.")

if __name__ == "__main__":
    main()

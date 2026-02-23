import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle  # NEW: For saving the model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Load the dataset
file_path = 'networkanomalydataset.csv'
df = pd.read_csv(file_path)

# 2. Separate features (X) and target label (y)
X = df.drop('Label', axis=1)
y = df['Label']

# 3. Split the data into training and testing sets (70% train, 30% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 4. Initialize and train the classification model
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# 5. Make predictions on the test set
y_pred = clf.predict(X_test)

# ==========================================
# Metrics & Visualizations
# ==========================================

# Print Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}\n")

# Print Classification Report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Plot Confusion Matrix using Seaborn
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=['Normal (0)', 'Anomaly (1)'],
    yticklabels=['Normal (0)', 'Anomaly (1)']
)
plt.title('Confusion Matrix', fontsize=16)
plt.xlabel('Predicted Label', fontsize=12)
plt.ylabel('True Label', fontsize=12)
plt.show()

# ==========================================
# Save the trained model as .pkl file
# ==========================================

model_filename = 'network_anomaly_model.pkl'

with open(model_filename, 'wb') as file:
    pickle.dump(clf, file)

print(f"\nModel saved successfully as {model_filename}")
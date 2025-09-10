import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------- CONFIG ----------------
GT_FILE = r"C:\cctv\ground_truth.csv"       # Ground truth CSV
PRED_FILE = r"C:\cctv\predictions.csv"      # Predictions CSV

# ---------------- LOAD DATA ----------------
def load_csv(path, ts_col, value_col):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    if ts_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"CSV must contain columns: '{ts_col}' and '{value_col}'")
    df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce', infer_datetime_format=True)
    df = df.dropna(subset=[ts_col, value_col])
    return df

gt_df = load_csv(GT_FILE, ts_col='timestamp', value_col='ground_truth')
pred_df = load_csv(PRED_FILE, ts_col='timestamp', value_col='prediction')

# ---------------- MERGE DATA ----------------
merged_df = pd.merge_asof(
    gt_df.sort_values('timestamp'),
    pred_df.sort_values('timestamp'),
    on='timestamp',
    direction='nearest',
    tolerance=pd.Timedelta(seconds=1)
)
merged_df = merged_df.dropna(subset=['ground_truth', 'prediction'])

y_true = merged_df['ground_truth'].astype(int)
y_pred = merged_df['prediction'].astype(int)

# ---------------- METRICS ----------------
# ---------------- METRICS ----------------
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
cm = confusion_matrix(y_true, y_pred)

print("===== Accuracy Metrics =====")
print(f"Accuracy : {acc*100:.2f}%")
print(f"Precision: {prec*100:.2f}%")
print(f"Recall   : {rec*100:.2f}%")
print(f"F1-Score : {f1*100:.2f}%")
print("Confusion Matrix:")
print(cm)


# ---------------- PLOT HEATMAP ----------------
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=[f'P{i}' for i in range(cm.shape[0])],
            yticklabels=[f'P{i}' for i in range(cm.shape[0])])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

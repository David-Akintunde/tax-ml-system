# ml-training/train_isolationforest.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib
import os

# Load dataset
df = pd.read_csv('tax_data.csv')
print(f"✅ Loaded {len(df)} records")

# Prepare features (same as before, but exclude the target 'fraud_label')
feature_cols = [
    'reported_income', 'deductions', 'taxable_income', 'tax_paid',
    'filing_delay_days', 'prior_audit_flag', 'net_profit_margin', 'debt_to_equity',
    'industry'
]
X = df[feature_cols]

# One-hot encode 'industry' (same as Random Forest)
X_encoded = pd.get_dummies(X, columns=['industry'], drop_first=False)

# True labels for evaluation (we have them, but Isolation Forest is unsupervised)
y_true = df['fraud_label']

# Train Isolation Forest (unsupervised, only on features)
iso_forest = IsolationForest(
    n_estimators=100,
    contamination=0.15,   # expected proportion of anomalies (matches our fraud rate)
    random_state=42,
    n_jobs=-1
)
iso_forest.fit(X_encoded)

# Predict anomalies (-1 for anomaly/fraud, 1 for normal)
y_pred_raw = iso_forest.predict(X_encoded)
# Convert to binary: 1 for fraud, 0 for normal (to match our labels)
y_pred = (y_pred_raw == -1).astype(int)

# Evaluate against true labels
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print("\n📊 Isolation Forest Performance (unsupervised vs true labels):")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

# Save model
os.makedirs('models', exist_ok=True)
joblib.dump(iso_forest, 'models/isolation_forest_model.pkl')
print("\n✅ Model saved to models/isolation_forest_model.pkl")
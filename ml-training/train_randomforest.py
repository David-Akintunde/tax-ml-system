# ml-training/train_randomforest.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os

# Load dataset
df = pd.read_csv('tax_data.csv')
print(f"✅ Loaded {len(df)} records")

# Define features (include 'industry' for encoding)
feature_cols = [
    'reported_income', 'deductions', 'taxable_income', 'tax_paid',
    'filing_delay_days', 'prior_audit_flag', 'net_profit_margin', 'debt_to_equity',
    'industry'   # <-- include industry now
]
X = df[feature_cols]
y = df['fraud_label']

# One-hot encode 'industry' (categorical)
X = pd.get_dummies(X, columns=['industry'], drop_first=False)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Training set: {len(X_train)} records, Test set: {len(X_test)} records")

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Predictions
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print("\n📊 Random Forest Performance:")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")
print(f"AUC-ROC:   {auc:.4f}")

# Feature importance
feature_importance = pd.DataFrame({'feature': X.columns, 'importance': rf.feature_importances_}).sort_values('importance', ascending=False)
print("\n🔍 Top 5 important features:")
print(feature_importance.head(5))

# Save model
os.makedirs('models', exist_ok=True)
joblib.dump(rf, 'models/random_forest_model.pkl')
print("\n✅ Model saved to models/random_forest_model.pkl")
# backend_api.py (with CORS)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os

# Paths
MODEL_DIR = "ml-training/models"
RF_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")
IF_PATH = os.path.join(MODEL_DIR, "isolation_forest_model.pkl")
LSTM_PATH = os.path.join(MODEL_DIR, "lstm_model.h5")

# Load models
rf_model = joblib.load(RF_PATH)
if_model = joblib.load(IF_PATH)
lstm_model = load_model(LSTM_PATH, compile=False)

# Load or create scaler for LSTM
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
if not os.path.exists(SCALER_PATH):
    df_rev = pd.read_csv("ml-training/monthly_revenue.csv")
    rev = df_rev['revenue'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaler.fit(rev)
    joblib.dump(scaler, SCALER_PATH)
else:
    scaler = joblib.load(SCALER_PATH)

# Define request models
class TaxpayerFeatures(BaseModel):
    reported_income: float
    deductions: float
    taxable_income: float
    tax_paid: float
    filing_delay_days: float
    prior_audit_flag: float
    net_profit_margin: float
    debt_to_equity: float
    industry_Manufacturing: float
    industry_Services: float
    industry_Telecom: float
    industry_Retail: float
    industry_Construction: float
    industry_Oil_Gas: float

class ForecastInput(BaseModel):
    last_12_months: List[float]

app = FastAPI(title="Tax Management ML API")

# ADD CORS MIDDLEWARE (allow React frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # React dev server
    allow_credentials=True,
    allow_methods=["*"],                       # Allow OPTIONS, POST, etc.
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Tax ML API is running"}

@app.post("/predict/risk")
def predict_risk(data: TaxpayerFeatures):
    try:
        features = np.array([
            data.reported_income,
            data.deductions,
            data.taxable_income,
            data.tax_paid,
            data.filing_delay_days,
            data.prior_audit_flag,
            data.net_profit_margin,
            data.debt_to_equity,
            data.industry_Manufacturing,
            data.industry_Services,
            data.industry_Telecom,
            data.industry_Retail,
            data.industry_Construction,
            data.industry_Oil_Gas
        ]).reshape(1, -1)
        
        prob = rf_model.predict_proba(features)[0][1]
        return {"risk_score": float(prob)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/fraud")
def predict_fraud(data: TaxpayerFeatures):
    try:
        features = np.array([
            data.reported_income,
            data.deductions,
            data.taxable_income,
            data.tax_paid,
            data.filing_delay_days,
            data.prior_audit_flag,
            data.net_profit_margin,
            data.debt_to_equity,
            data.industry_Manufacturing,
            data.industry_Services,
            data.industry_Telecom,
            data.industry_Retail,
            data.industry_Construction,
            data.industry_Oil_Gas
        ]).reshape(1, -1)
        
        score = if_model.decision_function(features)[0]
        anomaly = 1 / (1 + np.exp(-score))
        return {"anomaly_score": float(anomaly)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict/forecast")
def predict_forecast(data: ForecastInput):
    try:
        if len(data.last_12_months) != 12:
            raise ValueError("Need exactly 12 values")
        X_raw = np.array(data.last_12_months).reshape(1, -1, 1)
        X_scaled = scaler.transform(X_raw.reshape(-1, 1)).reshape(1, 12, 1)
        pred_scaled = lstm_model.predict(X_scaled, verbose=0)[0][0]
        pred_actual = scaler.inverse_transform([[pred_scaled]])[0][0]
        return {"forecast": float(pred_actual)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
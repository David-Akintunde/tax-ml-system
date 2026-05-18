# backend_api.py (with first_name, last_name)
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import re
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

# ---------- Configuration ----------
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ---------- Database Setup ----------
DATABASE_URL = "sqlite:///./tax_users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- Use pbkdf2_sha256 ----------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

security = HTTPBearer()

# ---------- User Model (split full_name) ----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    staff_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---------- Pydantic Schemas ----------
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    staff_id: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Profile schemas
class UserProfile(BaseModel):
    first_name: str
    last_name: str
    staff_id: str
    email: str
    created_at: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# ---------- Password Strength Validation ----------
def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")
    return True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# ---------- Load ML Models ----------
MODEL_DIR = "ml-training/models"
RF_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")
IF_PATH = os.path.join(MODEL_DIR, "isolation_forest_model.pkl")
LSTM_PATH = os.path.join(MODEL_DIR, "lstm_model.h5")

rf_model = joblib.load(RF_PATH)
if_model = joblib.load(IF_PATH)
lstm_model = load_model(LSTM_PATH, compile=False)

SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
if not os.path.exists(SCALER_PATH):
    df_rev = pd.read_csv("ml-training/monthly_revenue.csv")
    rev = df_rev['revenue'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaler.fit(rev)
    joblib.dump(scaler, SCALER_PATH)
else:
    scaler = joblib.load(SCALER_PATH)

# ---------- FastAPI App ----------
app = FastAPI(title="Tax Management ML API with Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Auth Endpoints ----------
@app.post("/auth/register", response_model=dict)
def register(user: UserRegister, db: Session = Depends(get_db)):
    validate_password_strength(user.password)

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.staff_id == user.staff_id).first():
        raise HTTPException(status_code=400, detail="Staff ID already registered")

    hashed = get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        staff_id=user.staff_id,
        email=user.email,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": authenticated_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------- Profile Endpoints ----------
@app.get("/auth/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserProfile(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        staff_id=current_user.staff_id,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )

@app.post("/auth/change-password")
def change_password(data: PasswordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password incorrect")
    validate_password_strength(data.new_password)
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# ---------- Protected ML Endpoints ----------
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

@app.post("/predict/risk")
def predict_risk(data: TaxpayerFeatures, current_user: User = Depends(get_current_user)):
    features = np.array([
        data.reported_income, data.deductions, data.taxable_income, data.tax_paid,
        data.filing_delay_days, data.prior_audit_flag, data.net_profit_margin, data.debt_to_equity,
        data.industry_Manufacturing, data.industry_Services, data.industry_Telecom,
        data.industry_Retail, data.industry_Construction, data.industry_Oil_Gas
    ]).reshape(1, -1)
    prob = rf_model.predict_proba(features)[0][1]
    return {"risk_score": float(prob)}

@app.post("/predict/fraud")
def predict_fraud(data: TaxpayerFeatures, current_user: User = Depends(get_current_user)):
    features = np.array([
        data.reported_income, data.deductions, data.taxable_income, data.tax_paid,
        data.filing_delay_days, data.prior_audit_flag, data.net_profit_margin, data.debt_to_equity,
        data.industry_Manufacturing, data.industry_Services, data.industry_Telecom,
        data.industry_Retail, data.industry_Construction, data.industry_Oil_Gas
    ]).reshape(1, -1)
    score = if_model.decision_function(features)[0]
    anomaly = 1 / (1 + np.exp(-score))
    return {"anomaly_score": float(anomaly)}

@app.post("/predict/forecast")
def predict_forecast(data: ForecastInput, current_user: User = Depends(get_current_user)):
    if len(data.last_12_months) != 12:
        raise HTTPException(status_code=400, detail="Need exactly 12 values")
    X_raw = np.array(data.last_12_months).reshape(1, -1, 1)
    X_scaled = scaler.transform(X_raw.reshape(-1, 1)).reshape(1, 12, 1)
    pred_scaled = lstm_model.predict(X_scaled, verbose=0)[0][0]
    pred_actual = scaler.inverse_transform([[pred_scaled]])[0][0]
    return {"forecast": float(pred_actual)}

@app.get("/")
def root():
    return {"message": "Tax ML API with Authentication (pbkdf2)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
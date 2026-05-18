# ml-training/train_lstm.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os

# Load data
df = pd.read_csv('monthly_revenue.csv', parse_dates=['date'])
revenue = df['revenue'].values.reshape(-1, 1)

# Scale to [0,1]
scaler = MinMaxScaler()
revenue_scaled = scaler.fit_transform(revenue)

# Create sequences for LSTM (use past 12 months to predict next month)
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

SEQ_LEN = 12
X, y = create_sequences(revenue_scaled, SEQ_LEN)

# Split: first 48 months for training, next 8 for validation, last ? for test (but we only have 60 total)
# Actually: total sequences = 60-12 = 48 sequences. Use 40 train, 8 test.
train_size = 40
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

# Build LSTM model
model = Sequential([
    LSTM(50, activation='relu', return_sequences=True, input_shape=(SEQ_LEN, 1)),
    Dropout(0.2),
    LSTM(50, activation='relu'),
    Dropout(0.2),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.summary()

# Early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train
history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=16,
    validation_data=(X_test, y_test),
    callbacks=[early_stop],
    verbose=1
)

# Predictions
y_pred_scaled = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred_scaled)
y_actual = scaler.inverse_transform(y_test)

# Metrics
mae = mean_absolute_error(y_actual, y_pred)
rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
print(f"\n📊 LSTM Forecast Performance:")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# Save model
os.makedirs('models', exist_ok=True)
model.save('models/lstm_model.h5')
print("✅ Model saved to models/lstm_model.h5")

# Optional: plot predictions
plt.plot(y_actual, label='Actual')
plt.plot(y_pred, label='Predicted')
plt.legend()
plt.title('Revenue Forecast vs Actual')
plt.savefig('lstm_forecast.png')
print("✅ Plot saved to lstm_forecast.png")
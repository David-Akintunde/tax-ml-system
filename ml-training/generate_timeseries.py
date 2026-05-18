# ml-training/generate_timeseries.py
import numpy as np
import pandas as pd

# Generate 5 years of monthly data (60 months) - use 'ME' for month end
np.random.seed(42)
months = pd.date_range(start='2019-01-01', periods=60, freq='ME')
month_num = np.arange(1, 61)

# Base trend: increasing revenue over time (e.g., 5% annual growth)
trend = 1e6 * (1 + 0.004 * month_num)  # ~0.4% monthly growth

# Seasonality: higher in Q2 and Q4 (tax deadlines)
seasonal = 1 + 0.2 * np.sin(2 * np.pi * month_num / 12 + np.pi/2)

# Random noise
noise = np.random.normal(1, 0.05, 60)

# Monthly revenue
revenue = trend * seasonal * noise
revenue = revenue.astype(int)

df_ts = pd.DataFrame({
    'date': months,
    'month': months.month,
    'year': months.year,
    'revenue': revenue
})

df_ts.to_csv('monthly_revenue.csv', index=False)
print("✅ Generated monthly_revenue.csv with 60 months of data")
print(df_ts.head())
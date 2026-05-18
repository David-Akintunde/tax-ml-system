# ml-training/generate_data.py
import numpy as np
import pandas as pd

np.random.seed(42)
n_records = 50000

# Taxpayer IDs
taxpayer_ids = [f"TX{i:06d}" for i in range(1, n_records + 1)]

# Industries
industries = ['Manufacturing', 'Services', 'Telecom', 'Retail', 'Construction', 'Oil & Gas']
industry = np.random.choice(industries, n_records, p=[0.20, 0.30, 0.10, 0.20, 0.15, 0.05])

# Financial features (legitimate baseline)
reported_income = np.random.uniform(1e6, 1e9, n_records)          # in Naira
deductions = np.random.uniform(0.05, 0.40, n_records) * reported_income
taxable_income = reported_income - deductions
tax_paid = taxable_income * 0.30   # 30% corporate tax rate

# Compliance history
filing_delay_days = np.random.exponential(10, n_records).astype(int)
prior_audit_flag = np.random.choice([0, 1], n_records, p=[0.85, 0.15])

# Synthetic fraud injection (15% of records)
fraud_flag = np.zeros(n_records, dtype=int)
n_fraud = int(n_records * 0.15)
fraud_indices = np.random.choice(n_records, n_fraud, replace=False)

# Manipulate fraudulent records: under-report income, overstate deductions
for idx in fraud_indices:
    reported_income[idx] = reported_income[idx] * np.random.uniform(0.60, 0.95)
    deductions[idx] = deductions[idx] * np.random.uniform(1.20, 1.60)
    taxable_income[idx] = reported_income[idx] - deductions[idx]
    tax_paid[idx] = taxable_income[idx] * 0.30
    fraud_flag[idx] = 1

# Additional features for risk scoring
net_profit_margin = (taxable_income / reported_income) * 100
debt_to_equity = np.random.uniform(0.2, 3.0, n_records)

# Create DataFrame
df = pd.DataFrame({
    'taxpayer_id': taxpayer_ids,
    'industry': industry,
    'reported_income': reported_income,
    'deductions': deductions,
    'taxable_income': taxable_income,
    'tax_paid': tax_paid,
    'filing_delay_days': filing_delay_days,
    'prior_audit_flag': prior_audit_flag,
    'net_profit_margin': net_profit_margin,
    'debt_to_equity': debt_to_equity,
    'fraud_label': fraud_flag   # 1 = fraudulent, 0 = legitimate
})

# Save to CSV
df.to_csv('tax_data.csv', index=False)
print(f"✅ Generated {n_records} records in tax_data.csv")
print(f"Fraud cases: {fraud_flag.sum()} ({fraud_flag.sum()/n_records*100:.1f}%)")
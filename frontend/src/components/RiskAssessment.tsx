import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { downloadCSV } from '../utils/exportCSV';
import AnimatedPage from './AnimatedPage';

const RiskAssessment = () => {
  const [formData, setFormData] = useState({
    reported_income: 5000000,
    deductions: 1000000,
    taxable_income: 4000000,
    tax_paid: 1200000,
    filing_delay_days: 5,
    prior_audit_flag: 0,
    net_profit_margin: 25,
    debt_to_equity: 1.2,
    industry_Manufacturing: 1,
    industry_Services: 0,
    industry_Telecom: 0,
    industry_Retail: 0,
    industry_Construction: 0,
    industry_Oil_Gas: 0,
  });
  const [result, setResult] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/predict/risk', formData);
      setResult(response.data.risk_score);
      toast.success('Risk prediction completed.');
    } catch (error) {
      console.error(error);
      toast.error('Error calling API. Ensure backend is running on port 5000.');
    }
    setLoading(false);
  };

  const handleExport = () => {
    if (result === null) {
      toast.error('Please run a prediction first.');
      return;
    }
    const exportData = [
      {
        ...formData,
        risk_score: result,
        prediction_date: new Date().toISOString(),
      },
    ];
    downloadCSV(exportData, `risk_assessment_${new Date().toISOString().slice(0, 19)}`);
    toast.success('Exported to CSV');
  };

  return (
    <AnimatedPage>
      <div className="bg-white p-6 rounded shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Risk Assessment (Random Forest)</h2>
          {result !== null && (
            <button
              onClick={handleExport}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-transform duration-200 hover:scale-105"
            >
              Export to CSV
            </button>
          )}
        </div>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          {Object.keys(formData).map((key) => (
            <div key={key}>
              <label className="block text-sm font-medium">{key}</label>
              <input
                type="number"
                step="any"
                name={key}
                value={formData[key as keyof typeof formData]}
                onChange={handleChange}
                className="mt-1 block w-full border rounded p-2"
              />
            </div>
          ))}
          <div className="col-span-2">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded transition-transform duration-200 hover:scale-105"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Predict Risk'}
            </button>
          </div>
        </form>
        {result !== null && (
          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h3 className="font-bold">Risk Score (probability of fraud):</h3>
            <p className="text-2xl">{result.toFixed(4)}</p>
            <p>{result > 0.5 ? '⚠️ High risk - consider audit' : '✅ Low risk'}</p>
          </div>
        )}
      </div>
    </AnimatedPage>
  );
};

export default RiskAssessment;